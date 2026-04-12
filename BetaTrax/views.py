from django.shortcuts import render, redirect, get_object_or_404
from .models import DefectReport, Developer, Product, Comment
from .serializers import (
    DefectReportSerializer, 
    EvaluateDefectSerializer, 
    DefectReportReadOnlySerializer,
    ProductSerializer,
    CommentSerializer
)
from rest_framework.response import Response
from rest_framework import generics, viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from .notification import send_defect_status_change_notification
from rest_framework.permissions import BasePermission 
from .permissions import IsProductOwner, IsDeveloper, IsBetaTester
from rest_framework.permissions import IsAuthenticated
# Create your views here.

#PBI-01 submit defect report =================================
# this is dashboard view function for tester
def dashboard_view(request):
    return render(request, "tester/dashboard.html" )

# handle the defect report form
class DefectReportCreateView(generics.CreateAPIView):
    queryset = DefectReport.objects.all()
    serializer_class = DefectReportSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect('defect_success')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# handle the successful form submission page
def defect_success_view(request):
    return render(request, 'tester/defect_success.html')

# PBI-02 Evaluate and accept defect for Product owner =================================
def owner_dashboard_view(request):
    return render(request, "owner/owner_dashboard.html" )

def evaluate_defect_page(request):
    defects = DefectReport.objects.filter(status='New')
    return render(request, 'owner/owner_evaluate_new.html', {'defects': defects})

class evaluate_defect_update_view(generics.RetrieveUpdateAPIView):
    queryset = DefectReport.objects.all()
    serializer_class = EvaluateDefectSerializer
    
# PBI-03 Select defect to work on =================================
def _resolve_developer_from_request(request):
    # Prefer authenticated identity when developer id matches user id.
    if request.user.is_authenticated:
        developer = Developer.objects.filter(pk=request.user.id).first()
        if developer:
            request.session['developer_id'] = developer.id
            return developer

    session_developer_id = request.session.get('developer_id')
    if session_developer_id:
        developer = Developer.objects.filter(pk=session_developer_id).first()
        if developer:
            return developer

    query_developer_id = request.GET.get('developer_id')
    if query_developer_id:
        developer = get_object_or_404(Developer, pk=query_developer_id)
        request.session['developer_id'] = developer.id
        return developer

    developer = Developer.objects.first()
    if developer:
        request.session['developer_id'] = developer.id
    return developer


def developer_dashboard_view(request):
    developer = _resolve_developer_from_request(request)

    defects = DefectReport.objects.none()
    if developer:
        defects = DefectReport.objects.filter(
            product=developer.product,
            status=DefectReport.CurrentStatus.OPEN,
            developer__isnull=True,
        ).order_by('id')

    return render(
        request,
        'developer/dashboard.html',
        {'defects': defects, 'developer': developer},
    )


def assign_defect_view(request, pk):
    if request.method != 'POST':
        return redirect('developer_dashboard')

    developer = _resolve_developer_from_request(request)
    if not developer:
        return redirect('developer_dashboard')

    defect = get_object_or_404(DefectReport, pk=pk)

    if defect.product_id == developer.product_id and defect.status == DefectReport.CurrentStatus.OPEN:
        defect.status = DefectReport.CurrentStatus.ASSIGNED
        defect.developer = developer
        defect.save(update_fields=['status', 'developer'])

    return redirect(f"/developer/?developer_id={developer.id}")

#PBI-06
class NewDefectListView(generics.ListAPIView):
    serializer_class = DefectReportReadOnlySerializer
    def get_queryset(self):
        return DefectReport.objects.filter(status=DefectReport.CurrentStatus.NEW)

class DefectDetailView(generics.RetrieveAPIView):
    queryset = DefectReport.objects.all()
    serializer_class = DefectReportReadOnlySerializer

# Helper function to get defect or return 404
def get_defect_or_404(pk):
    try:
        return DefectReport.objects.get(pk=pk)
    except DefectReport.DoesNotExist:
        return None

# FilterSet for DefectReport to support filtering
# api/defects/ is the url showing all the defects
class DefectReportViewSet(viewsets.ModelViewSet):
    queryset = DefectReport.objects.all()
    serializer_class = DefectReportSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['severity', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'status']

    # Override get_queryset to handle case-insensitive status filtering
    # For example: api/defects/?status=fixed
    # We use ?status=fixed that would show defects status = 'fixed'
    
    #PBI-02 evaluate
    def get_serializer_class(self):
        if self.action == 'evaluate':
            return EvaluateDefectSerializer
        return DefectReportSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            # url no lowercase so capitalize here to aviod changing the model.py stored choice values
            normalized = status_param.capitalize()
            queryset = queryset.filter(status=normalized)
        #PBI-07 exclude the rejected defect reports from the list
        else:
            queryset = queryset.exclude(status=DefectReport.CurrentStatus.REJECTED)
        return queryset

    #PBI-02 evaluate
    @action(detail=True, methods=['patch'])
    def evaluate(self, request, pk=None):
        defect = self.get_object()
        if defect.status != DefectReport.CurrentStatus.NEW:
            return Response({"error": "Only NEW defects can be evaluated"}, status=400)
        serializer = EvaluateDefectSerializer(defect, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    # PBI-07: Reject defect
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsProductOwner])
    def reject(self, request, pk=None):
        """Product owner rejects an invalid defect report."""
        defect = self.get_object()
        
        # Check permission
        if defect.productowner != request.user.productowner:
            return Response({'error': 'No permission'}, status=status.HTTP_403_FORBIDDEN)
        
        if defect.status not in [DefectReport.CurrentStatus.NEW, DefectReport.CurrentStatus.OPEN]:
            return Response(
                {'error': f'Cannot reject status {defect.status}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = defect.status
        defect.status = DefectReport.CurrentStatus.REJECTED
        send_defect_status_change_notification(defect, old_status, defect.status)
        defect.save()
        
        serializer = DefectReportReadOnlySerializer(defect)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # PBI-08: Mark as duplicate
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsProductOwner])
    def mark_duplicate(self, request, pk=None):
        """Product owner marks a defect as duplicated."""
        defect = self.get_object()
        
        # Check permission
        if defect.productowner != request.user.productowner:
            return Response({'error': 'No permission'}, status=status.HTTP_403_FORBIDDEN)
        
        if defect.status not in [DefectReport.CurrentStatus.NEW, DefectReport.CurrentStatus.OPEN]:
            return Response(
                {'error': f'Cannot mark duplicate status {defect.status}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = EvaluateDefectSerializer(defect, data=request.data, partial=True)
        if serializer.is_valid():
            old_status = defect.status
            serializer.validated_data['status'] = DefectReport.CurrentStatus.DUPLICATED
            updated_defect = serializer.save()
            
            send_defect_status_change_notification(updated_defect, old_status, updated_defect.status)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # PBI-04: Fix defect
    # For example: api/defects/1/ we can see the details of the defect report with id=1
    # We have a select button to trigger action (fix/resolve) called "Extra Action"
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsDeveloper])
    def fix(self, request, pk=None):
        defect = self.get_object()
        old_status = defect.status
        if defect.status != DefectReport.CurrentStatus.ASSIGNED:
            return Response(
                {'error': 'Only defects with status "Assigned" can be marked as fixed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        defect.status = DefectReport.CurrentStatus.FIXED
        send_defect_status_change_notification(defect, old_status, defect.status)
        defect.save()
        serializer = DefectReportReadOnlySerializer(defect)
        return Response(serializer.data)
    
    # PBI-10: Cannot reproduce defect
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsDeveloper])
    def cannot_reproduce(self, request, pk=None):
        defect = self.get_object()
        old_status = defect.status
        if defect.status != DefectReport.CurrentStatus.ASSIGNED:
            return Response(
                {'error': 'Only defects with status "Assigned" can be marked as cannot reproduce.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        defect.status = DefectReport.CurrentStatus.CANNOT_REPRODUCE
        send_defect_status_change_notification(defect, old_status, defect.status)
        defect.save()
        serializer = DefectReportReadOnlySerializer(defect)
        return Response(serializer.data)

    # PBI-05: Resolve defect
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsProductOwner])
    def resolve(self, request, pk=None):
        defect = self.get_object()
        old_status = defect.status
        if defect.status != DefectReport.CurrentStatus.FIXED:
            return Response(
                {'error': 'Only defects with status "Fixed" can be resolved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        defect.status = DefectReport.CurrentStatus.RESOLVED
        send_defect_status_change_notification(defect, old_status, defect.status)
        defect.save()
        serializer = DefectReportReadOnlySerializer(defect)
        return Response(serializer.data)
    
    # PBI-11: Reopen defect
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsProductOwner])
    def reopen(self, request, pk=None):
        defect = self.get_object()
        old_status = defect.status
        if defect.status != DefectReport.CurrentStatus.FIXED:
            return Response(
                {'error': 'Only defects with status "Fixed" can be reopened.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        defect.status = DefectReport.CurrentStatus.REOPENED
        # clear the assigned developer when reopening a defect
        defect.developer = None
        send_defect_status_change_notification(defect, old_status, defect.status)
        defect.save()
        serializer = DefectReportReadOnlySerializer(defect)
        return Response(serializer.data)

#PBI-09 Product Viewset
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:  # GET methods
            return [IsAuthenticated()]  # Any authenticated user can view
        else:  # POST, PATCH, DELETE
            return [IsProductOwner()]  # Only product owners can modify

# PBI-12 Comment ViewSet
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get comments for a specific defect"""
        defect_id = self.kwargs.get('defect_pk')
        return Comment.objects.filter(defect_id=defect_id)
    
    def perform_create(self, serializer):
        """Save comment with defect reference"""
        defect_id = self.kwargs.get('defect_pk')
        serializer.save(defect_id=defect_id)
