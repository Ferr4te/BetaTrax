from django.urls import path
from . import views
from .views import DefectReportCreateView
from .views import evaluate_defect_update_view, fix_defect, resolve_defect#, close_defect_update_view

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

    #PBI-03 Select defect to work on
    path('developer/', views.developer_dashboard_view, name='developer_dashboard'),
    path('developer/defects/<int:pk>/assign/', views.assign_defect_view, name='assign_defect'),

    #PBI-04: Fix defect
    path('defects/<int:pk>/fix/', views.fix_defect, name='fix_defect'),
    
    #PBI-05: Resolve defect
    path('defects/<int:pk>/resolve/', views.resolve_defect, name='resolve_defect'),
]
