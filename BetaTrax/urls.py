from django.urls import path, include
from . import views
from .views import DefectReportCreateView, DefectReportViewSet, ProductViewSet, CommentViewSet
from .views import evaluate_defect_update_view
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Register the viewset with a router
router = DefaultRouter()
router.register(r'defects', DefectReportViewSet, basename = 'defect')
router.register(r'products', ProductViewSet, basename='product')

# Nested Router for Comments
defect_router = routers.NestedDefaultRouter(router, 'defects', lookup='defect')
defect_router.register('comments', CommentViewSet, basename='defect-comment')

#login as tester
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include(defect_router.urls)),

    #API documentation endpoint
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/',SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Delete url for PBI-04 and PBI-05 since fix and resolve inside
    # DefectReportViewSet already can access to PBI-04 and PBI-05 pages

    #PBI-06
    path('api/defects/new/', views.NewDefectListView.as_view(), name='new_defects'),
    path('api/defects/<int:pk>/', views.DefectDetailView.as_view(), name='defect_detail'),
]
