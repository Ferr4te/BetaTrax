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
    
    # old method removed, this is for adding new defect
    # with the same route: GET /api/defects/new/
    @action(detail=False, methods=['get'], url_path='new')
    def new_defects(self, request):
        queryset = self.get_queryset().filter(status=DefectReport.CurrentStatus.NEW)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)    

    #PBI-02 evaluate
    def get_serializer_class(self):
        if self.action == 'evaluate':
            return EvaluateDefectSerializer
        elif self.action in ['fix', 'resolve', 'assign', 'cannot_reproduce', 'reopen']:
            return DefectReportReadOnlySerializer
        else:
            return DefectReportReadOnlySerializer
    
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

    # PBI-03: Assign
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsDeveloper])
    def assign(self, request, pk=None):
        defect = self.get_object()
        developer = request.user.developer
    
        if defect.product_id != developer.product_id:
            return Response({'error': 'Not your product'}, status=403)
    
        if defect.status != DefectReport.CurrentStatus.OPEN:
            return Response({'error': 'Only OPEN defects can be assigned'}, status=400)
    
        if defect.developer:
            return Response({'error': 'Already assigned'}, status=400)
    
        old_status = defect.status
        defect.status = DefectReport.CurrentStatus.ASSIGNED
        defect.developer = developer
        defect.save()
        send_defect_status_change_notification(defect, old_status, defect.status)
    
        return Response({'message': 'Assigned successfully'})
    
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
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsDeveloper])
    def fix(self, request, pk=None):
        defect = self.get_object()

        if defect.status != DefectReport.CurrentStatus.ASSIGNED:
            return Response(
                {'error': 'Only defects with status "Assigned" can be marked as fixed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = defect.status
        defect.status = DefectReport.CurrentStatus.FIXED
        send_defect_status_change_notification(defect, old_status, defect.status)
        defect.save()

        serializer = DefectReportReadOnlySerializer(defect)
        return Response(serializer.data)
    
    # PBI-10: Cannot reproduce defect
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsDeveloper])
    def cannot_reproduce(self, request, pk=None):
        defect = self.get_object()
        
        if defect.status != DefectReport.CurrentStatus.ASSIGNED:
            return Response(
                {'error': 'Only defects with status "Assigned" can be marked as cannot reproduce.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = defect.status
        defect.status = DefectReport.CurrentStatus.CANNOT_REPRODUCE
        send_defect_status_change_notification(defect, old_status, defect.status)
        defect.save()
        serializer = DefectReportReadOnlySerializer(defect)
        return Response(serializer.data)

    # PBI-05: Resolve defect
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsProductOwner])
    def resolve(self, request, pk=None):
        defect = self.get_object()
        
        if defect.status != DefectReport.CurrentStatus.FIXED:
            return Response(
                {'error': 'Only defects with status "Fixed" can be resolved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = defect.status
        defect.status = DefectReport.CurrentStatus.RESOLVED
        send_defect_status_change_notification(defect, old_status, defect.status)
        defect.save()
        serializer = DefectReportReadOnlySerializer(defect)
        return Response(serializer.data)
    
    # PBI-11: Reopen defect
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsProductOwner])
    def reopen(self, request, pk=None):
        defect = self.get_object()
        
        if defect.status != DefectReport.CurrentStatus.FIXED:
            return Response(
                {'error': 'Only defects with status "Fixed" can be reopened.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = defect.status
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

#PBI-18
class DeveloperEffectivenessViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsProductOwner]
    
    def get_developer_metrics(self, developer):
        """Get effectiveness metrics for a single developer"""
        metrics = developer.get_effectiveness_metrics()
        
        return {
            'developer_id': developer.id,
            'developer_name': developer.user.username,
            'total_fixed': metrics['fixed_count'],
            'total_reopened': metrics['reopened_count'],
            'ratio': metrics['ratio'],
            'classification': metrics['classification'],
            'message': metrics.get('message')
        }

    @action(detail=False, methods=['get'], url_path='effectiveness/(?P<developer_id>[^/.]+)')
    def developer_effectiveness(self, request, developer_id=None):
        # Verify product owner has access to this developer's product
        try:
            developer = get_object_or_404(Developer, id=developer_id)
        except ValueError:
            return Response(
                {'error': 'Invalid developer ID format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the requesting product owner belongs to the same product
        if not request.user.is_superuser:
            if not hasattr(request.user, 'productowner'):
                return Response(
                    {'error': 'You do not have permission to view developer metrics'},
                    status=status.HTTP_403_FORBIDDEN
                )
            if request.user.productowner.product_id != developer.product_id:
                return Response(
                    {'error': 'You can only view developers from your own product'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        metrics_data = self.get_developer_metrics(developer)
        serializer = DeveloperEffectivenessSerializer(metrics_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='effectiveness')
    def all_developers_effectiveness(self, request):
        # Determine which developers to show
        if request.user.is_superuser:
            developers = Developer.objects.all()
        else:
            if not hasattr(request.user, 'productowner'):
                return Response(
                    {'error': 'You do not have permission to view developer metrics'},
                    status=status.HTTP_403_FORBIDDEN
                )
            developers = Developer.objects.filter(product=request.user.productowner.product)
        
        results = []
        for developer in developers:
            metrics_data = self.get_developer_metrics(developer)
            results.append(metrics_data)
        
        # Sort by ratio (worst first for visibility)
        results.sort(key=lambda x: x['ratio'] if x['ratio'] is not None else float('inf'), reverse=True)
        
        serializer = DeveloperEffectivenessSerializer(results, many=True)
        
        # Add summary statistics
        summary = self._get_summary_statistics(results)
        
        return Response({
            'developers': serializer.data,
            'summary': summary
        })

    def _get_summary_statistics(self, metrics_list):
        """Calculate summary statistics from metrics list"""
        valid_metrics = [m for m in metrics_list if m['ratio'] is not None]
        
        if not valid_metrics:
            return {
                'total_developers': len(metrics_list),
                'developers_with_sufficient_data': 0,
                'average_ratio': None,
                'good_count': 0,
                'fair_count': 0,
                'poor_count': 0,
                'insufficient_count': len([m for m in metrics_list if m['ratio'] is None])
            }
        
        good_count = len([m for m in valid_metrics if m['classification'] == 'Good'])
        fair_count = len([m for m in valid_metrics if m['classification'] == 'Fair'])
        poor_count = len([m for m in valid_metrics if m['classification'] == 'Poor'])
        
        avg_ratio = sum(m['ratio'] for m in valid_metrics) / len(valid_metrics)
        
        return {
            'total_developers': len(metrics_list),
            'developers_with_sufficient_data': len(valid_metrics),
            'average_ratio': round(avg_ratio, 6),
            'good_count': good_count,
            'fair_count': fair_count,
            'poor_count': poor_count,
            'insufficient_count': len([m for m in metrics_list if m['ratio'] is None])
        }

class DeveloperViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Developer.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Developer.objects.all()
        if hasattr(user, 'productowner'):
            return Developer.objects.filter(product=user.productowner.product)
        return Developer.objects.none()
    
    @action(detail=True, methods=['get'], url_path='effectiveness')
    def effectiveness(self, request, pk=None):
        developer = self.get_object()
        
        # Check permission
        if not request.user.is_superuser:
            if hasattr(request.user, 'productowner'):
                if request.user.productowner.product_id != developer.product_id:
                    return Response(
                        {'error': 'You can only view developers from your own product'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                return Response(
                    {'error': 'You do not have permission to view developer metrics'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        metrics = developer.get_effectiveness_metrics()
        
        response_data = {
            'developer_id': developer.id,
            'developer_name': developer.user.username,
            'developer_email': developer.user.email,
            'product_id': developer.product.id,
            'product_name': developer.product.name if developer.product.name else f"Product {developer.product.id}",
            'total_fixed': metrics['fixed_count'],
            'total_reopened': metrics['reopened_count'],
            'ratio': metrics['ratio'],
            'classification': metrics['classification'],
        }
        
        if metrics.get('message'):
            response_data['message'] = metrics['message']
        
        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='effectiveness/all')
    def all_effectiveness(self, request):
        if request.user.is_superuser:
            developers = Developer.objects.all()
        elif hasattr(request.user, 'productowner'):
            developers = Developer.objects.filter(product=request.user.productowner.product)
        else:
            return Response(
                {'error': 'You do not have permission to view developer metrics'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        results = []
        for developer in developers:
            metrics = developer.get_effectiveness_metrics()
            results.append({
                'developer_id': developer.id,
                'developer_name': developer.user.username,
                'total_fixed': metrics['fixed_count'],
                'total_reopened': metrics['reopened_count'],
                'ratio': metrics['ratio'],
                'classification': metrics['classification'],
            })
        
        # Calculate summary
        valid_results = [r for r in results if r['ratio'] is not None]
        summary = {
            'total_developers': len(results),
            'developers_with_sufficient_data': len(valid_results),
            'good_count': len([r for r in valid_results if r['classification'] == 'Good']),
            'fair_count': len([r for r in valid_results if r['classification'] == 'Fair']),
            'poor_count': len([r for r in valid_results if r['classification'] == 'Poor']),
        }
        
        if valid_results:
            summary['average_ratio'] = round(
                sum(r['ratio'] for r in valid_results) / len(valid_results), 6
            )
        else:
            summary['average_ratio'] = None
        
        return Response({
            'developers': results,
            'summary': summary
        })
