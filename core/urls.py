from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import TenantViewSet, UserViewSet

router = DefaultRouter()
router.register(r'tenants', TenantViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
