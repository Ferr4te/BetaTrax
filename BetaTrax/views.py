from django.shortcuts import render, redirect, get_object_or_404
from .models import DefectReport
from .forms import DefectReportSerializer
from rest_framework.response import Response
from rest_framework import generics
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

# PBI 4 dashboard view for developer =================================
def developer_dashboard(request):
    defects = DefectReport.objects.filter(assigned_to=request.user, status='ASSIGNED')

    return render(request, 'developer/dashboard.html', {'defects': defects})

# PBI 4 handle fixing a defect
def fix_defect(request, defect_id):
    defect = get_object_or_404(DefectReport, id=defect_id, assigned_to=request.user, status='ASSIGNED')

    if request.method == 'POST':
        defect.status = 'FIXED'
        defect.save()
        return redirect('developer_dashboard')
    
    return render(request, 'developer/fix_confirm.html', {'defect': defect})
