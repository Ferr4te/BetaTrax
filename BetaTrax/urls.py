from django.urls import path
from . import views

#login as tester
urlpatterns = [
    #login as tester
    #PBI-01 submite defect report
    path('tester/', views.dashboard_view, name="tester_dashboard"),
    path('tester/defectform/', DefectReportCreateView.as_view(),name='defect_form'),
    path('defectform/success/', views.defect_success_view, name="defect_success"),
    # PBI 4 developer dashboard and fix defect
    path('developer/dashboard/', views.developer_dashboard, name='developer_dashboard'),
    path('developer/fix/<int:defect_id>/', views.fix_defect, name='fix_defect'),
]
