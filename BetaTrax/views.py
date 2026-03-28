from django.shortcuts import render, HttpResponse, redirect
from .forms import DefectForm
from .models import DefectReport, Product
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

# PBl-01 (Trying)
def evaluate_defect(request):
    product = Product.objects.first()
    title = request.data.get('title')
    description = request.data.get('description')
    reproduce_step = request.data.get('reproduce_step')
    version = request.data.get('version')
    tester_email = request.data.get('tester_email', '')

    report = DefectReport.objects.create(
        product=product,
        title=title,
        description=description,
        reproduce_step=reproduce_step,
        version=version,
        tester_email=tester_email,
        status='New'
    )
    
    return 0

# PBL-02 (Trying)
def evaluate_defect(request, pk):
    try:
        report = DefectReport.objects.get(pk=pk)
    except DefectReport.DoesNotExist:
        return HttpResponse("Defect report not found.", status=404)
    
    report.status = 'Open'
    report.save()

    return 0

# PBL-03 (Trying)
def assign_defect(request, pk):
    try:
        report = DefectReport.objects.get(pk=pk)
    except DefectReport.DoesNotExist:
        return HttpResponse("Defect report not found.", status=404)
    
    report.status = 'Assigned'
    report.save()

    return 0

# PBL-04 (Trying)
def mark_fixed(request, pk):
    try:
        report = DefectReport.objects.get(pk=pk)
    except DefectReport.DoesNotExist:
        return HttpResponse("Defect report not found.", status=404)
    
    report.status = 'Fixed'
    report.save()

    return 0

# PBL-05 (Trying)
def mark_resolved(request, pk):
    try:
        report = DefectReport.objects.get(pk=pk)
    except DefectReport.DoesNotExist:
        return HttpResponse("Defect report not found.", status=404)
    
    report.status = 'Resolved'
    report.save()

    return 0