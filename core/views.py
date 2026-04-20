from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from rest_framework import viewsets, permissions
from core.models import Tenant, User
from core.forms import TenantBrandingForm
from core.serializers import TenantSerializer, UserSerializer
from core.permissions import IsSuperAdmin, IsTenantAdmin, TenantQuerysetMixin
from assets.models import Tank, PipelineSegment, Depot
from operations.models import Batch, VesselDischarge
from django.db.models import Count, Sum


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        tenant = self.request.tenant
        
        # Base querysets
        tanks_qs = Tank.objects.all()
        depots_qs = Depot.objects.all()
        segments_qs = PipelineSegment.objects.all()
        batches_qs = Batch.objects.all()

        if tenant:
            tanks_qs = tanks_qs.filter(depot__tenant=tenant)
            depots_qs = depots_qs.filter(tenant=tenant)
            segments_qs = segments_qs.filter(tenant=tenant)
            batches_qs = batches_qs.filter(segment__tenant=tenant)
        elif not user.is_superuser:
            # Not a superuser and no tenant? See nothing.
            tanks_qs = tanks_qs.none()
            depots_qs = depots_qs.none()
            segments_qs = segments_qs.none()
            batches_qs = batches_qs.none()

        # Summary Stats
        context['total_tanks'] = tanks_qs.count()
        context['total_depots'] = depots_qs.count()
        context['flowing_segments'] = segments_qs.filter(status='FLOWING').count()
        context['active_batches'] = batches_qs.filter(status='IN_TRANSIT').count()
        
        # Tank Utilization
        tanks_with_depot = tanks_qs.select_related('depot')
        agg = tanks_with_depot.aggregate(
            total_vol=Sum('current_volume'),
            total_cap=Sum('safe_fill_capacity')
        )
        total_vol = agg['total_vol'] or 0
        total_cap = agg['total_cap'] or 0
        context['avg_utilization'] = (total_vol / total_cap * 100) if total_cap > 0 else 0
        
        context['top_tanks'] = tanks_with_depot.order_by('-current_volume')[:5]
        context['active_batches_list'] = batches_qs.filter(
            status='IN_TRANSIT'
        ).select_related('segment', 'product_type')[:10]
        
        return context


class TenantViewSet(viewsets.ModelViewSet):
    """CRUD for Tenants — Super Admin only."""
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]


class UserViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    """CRUD for users within a tenant. Tenant admins can manage their users."""
    queryset = User.objects.select_related('tenant').all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantAdmin]
    filterset_fields = ['role', 'is_active']
class TenantSettingsView(LoginRequiredMixin, UpdateView):
    model = Tenant
    form_class = TenantBrandingForm
    template_name = 'core/settings.html'
    success_url = reverse_lazy('tenant_settings')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from alerts.models import AlertRule
        context['alert_rules'] = AlertRule.objects.filter(tenant=self.request.tenant)
        return context

    def get_object(self, queryset=None):
        return self.request.tenant

from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin

class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'account/profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self, queryset=None):
        return self.request.user

class CustomPasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = 'account/password_change.html'
    success_url = reverse_lazy('profile')
    success_message = "Your password was changed successfully."

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required
@require_POST
def toggle_theme(request):
    user = request.user
    new_theme = request.POST.get('theme')
    if new_theme in ['light', 'dark']:
        user.theme_preference = new_theme
        user.save(update_fields=['theme_preference'])
        return JsonResponse({'status': 'success', 'theme': user.theme_preference})
    return JsonResponse({'status': 'error'}, status=400)
