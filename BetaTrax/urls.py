from django.urls import path
from . import views

#login as tester
urlpatterns = [
    path('', views.dashboard_view, name="dashboard"),
    path('defectform/', views.defect_view, name="defectform"),
    path('defectform/success/', views.defect_success_view, name="defect-success"),
    # PBI 4 developer dashboard and fix defect
    path('developer/dashboard/', views.developer_dashboard, name='developer_dashboard'),
    path('developer/fix/<int:defect_id>/', views.fix_defect, name='fix_defect'),
]
