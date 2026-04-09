from django.urls import path, include
from . import views
from .views import DefectReportCreateView, DefectReportViewSet
from .views import evaluate_defect_update_view#, close_defect_update_view
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'defects', DefectReportViewSet)

#login as tester
urlpatterns = [
    path('api/', include(router.urls)),
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

    # Delete url for PBI-04 and PBI-05 since fix and resolve inside
    # DefectReportViewSet already can access to PBI-04 and PBI-05 pages

    #PBI-06
    path('api/defects/new/', views.NewDefectListView.as_view(), name='new_defects'),
    path('api/defects/<int:pk>/', views.DefectDetailView.as_view(), name='defect_detail'),
]
