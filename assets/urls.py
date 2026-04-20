from django.urls import path, include
from rest_framework.routers import DefaultRouter
from assets.views import (
    ProductTypeViewSet, DepotViewSet, TankViewSet, PipelineSegmentViewSet,
    TankListView, PipelineListView, TankCreateView, PipelineCreateView,
    TankDetailView, PipelineDetailView
)

router = DefaultRouter()
router.register(r'products', ProductTypeViewSet)
router.register(r'depots', DepotViewSet)
router.register(r'tanks', TankViewSet)
router.register(r'segments', PipelineSegmentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('tanks/', TankListView.as_view(), name='tank_list'),
    path('tanks/add/', TankCreateView.as_view(), name='tank_add'),
    path('tanks/<int:pk>/', TankDetailView.as_view(), name='tank_detail'),
    path('segments/', PipelineListView.as_view(), name='pipeline_list'),
    path('segments/add/', PipelineCreateView.as_view(), name='pipeline_add'),
    path('segments/<int:pk>/', PipelineDetailView.as_view(), name='pipeline_detail'),
]
