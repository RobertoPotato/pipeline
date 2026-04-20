from django.urls import path, include
from rest_framework.routers import DefaultRouter
from operations.views import (
    BatchViewSet, BatchHistoryViewSet, VesselDischargeViewSet,
    BatchListView, BatchCreateView, BatchDetailView
)

router = DefaultRouter()
router.register(r'batches', BatchViewSet)
router.register(r'batch-history', BatchHistoryViewSet)
router.register(r'vessels', VesselDischargeViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('batches/', BatchListView.as_view(), name='batch_list'),
    path('batches/add/', BatchCreateView.as_view(), name='batch_add'),
    path('batches/<int:pk>/', BatchDetailView.as_view(), name='batch_detail'),
]
