from django.shortcuts import render, redirect
from .models import DefectReport
from .forms import DefectReportSerializer
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action, api_view
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

# PBI-04 Fix defect
@api_view(['POST'])
def defect_fix(request, pk):
    defect = get_defect_or_404(pk)
    if defect is None:
        return Response({'error': 'Defect not found'}, status=status.HTTP_404_NOT_FOUND)

    if defect.status != 'ASSIGNED':
        return Response({'error': 'Only defects status in "Assigned" can be marked as fixed.'},
                        status=status.HTTP_400_BAD_REQUEST)

    defect.status = 'FIXED'
    defect.save()

    serializer = DefectReportSerializer(defect)
    return Response(serializer.data)

# Helper function to get defect or return 404
def get_defect_or_404(pk):
    try:
        return DefectReport.objects.get(pk=pk)
    except DefectReport.DoesNotExist:
        return None
