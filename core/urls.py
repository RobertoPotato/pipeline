from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    TenantViewSet, UserViewSet, 
    UserProfileView, CustomPasswordChangeView,
    toggle_theme
)

router = DefaultRouter()
router.register(r'tenants', TenantViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('toggle-theme/', toggle_theme, name='toggle_theme'),
]
