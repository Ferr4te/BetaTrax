from django.urls import path
from . import views

#login as tester
urlpatterns = [
    path('', views.dashboard_view, name="dashboard"),
    path('defectform/', views.defect_view, name="defectform"),
    path('defectform/success/', views.defect_success_view, name="defect-success"),
]
