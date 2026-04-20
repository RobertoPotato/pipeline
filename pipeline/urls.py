"""
Main URL configuration for the PipelineGuard project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import DashboardView, TenantSettingsView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('settings/', TenantSettingsView.as_view(), name='tenant_settings'),
    path('admin/', admin.site.urls),

    # App endpoints (Templates + API)
    path('core/', include('core.urls')),
    path('assets/', include('assets.urls')),
    path('operations/', include('operations.urls')),
    path('telemetry/', include('telemetry.urls')),
    path('alerts/', include('alerts.urls')),

    # DRF browsable API auth
    path('api-auth/', include('rest_framework.urls')),

    # django-allauth
    path('accounts/', include('allauth.urls')),

    # Plotly Dash
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
