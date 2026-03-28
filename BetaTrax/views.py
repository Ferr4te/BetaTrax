from django.shortcuts import render, HttpResponse, redirect
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
