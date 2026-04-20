from django.urls import path, include
from rest_framework.routers import DefaultRouter
from telemetry.views import ApiIngestionLogViewSet

router = DefaultRouter()
router.register(r'logs', ApiIngestionLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
