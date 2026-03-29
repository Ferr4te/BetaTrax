from django.urls import path
from . import views

#login as tester
urlpatterns = [
    #login as tester
    #PBI-01 submite defect report
    path('tester/', views.dashboard_view, name="tester_dashboard"),
    path('tester/defectform/', DefectReportCreateView.as_view(),name='defect_form'),
    path('defectform/success/', views.defect_success_view, name="defect_success"),
    
    #PBI-02 Evaluate and accept defect for Product owner =================================
    path('owner/', views.owner_dashboard_view, name="owner_dashboard"),
    path('owner/evaluate/', views.evaluate_defect_page, name="owner_defect"),
    path('owner/evaluate/<int:pk>/', evaluate_defect_update_view.as_view(), name="owner_defect_evaluate"),


    # PBI 4 developer dashboard and fix defect
    path('developer/dashboard/', views.developer_dashboard, name='developer_dashboard'),
    path('developer/fix/<int:defect_id>/', views.fix_defect, name='fix_defect'),
]
