from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .forms import DefectForm
from .models import DefectReport
# Create your views here.

# this is dashboard view function for tester
def dashboard_view(request):
    return render(request, "tester/dashboard.html" )

# handle the defect report form
def defect_view(request):
    if request.method == "POST":
        form = DefectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('defect-success')
    else:
        form = DefectForm()
    context = {'form': form}
    return render(request, 'tester/defectform.html', context)

# handle the successful form submission page
def defect_success_view(request):
    return render(request, 'tester/defect_success.html')

# PBI 4 dashboard view for developer
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