from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from core.models import Tenant
from core.forms import AlertRuleForm
from alerts.models import AlertRule, Notification
from alerts.serializers import AlertRuleSerializer, NotificationSerializer
from core.permissions import IsTenantUser, IsTenantAdmin, TenantQuerysetMixin


class AlertRuleViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    permission_classes = [IsTenantAdmin]
    filterset_fields = ['entity_type', 'is_active']
    search_fields = ['name', 'metric']


class NotificationViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Notification.objects.select_related('rule').all().order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = [IsTenantUser]
    filterset_fields = ['is_read']

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """POST /api/alerts/notifications/mark-all-read/"""
        tenant = request.tenant
        count = Notification.objects.filter(tenant=tenant, is_read=False).update(is_read=True)
        return Response({'marked_read': count})

    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        """POST /api/alerts/notifications/{id}/read/"""
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notification).data)

# Template Views
class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'alerts/notification_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        user = self.request.user
        tenant = self.request.tenant
        if tenant:
            qs = Notification.objects.filter(tenant=tenant)
        elif user.is_superuser:
            qs = Notification.objects.all()
        else:
            qs = Notification.objects.none()
        return qs.select_related('rule').order_by('-created_at')


class AlertRuleListView(LoginRequiredMixin, ListView):
    model = AlertRule
    template_name = 'alerts/rule_list.html'
    context_object_name = 'rules'

    def get_queryset(self):
        user = self.request.user
        tenant = self.request.tenant
        if tenant:
            qs = AlertRule.objects.filter(tenant=tenant)
        elif user.is_superuser:
            qs = AlertRule.objects.all()
        else:
            qs = AlertRule.objects.none()
        return qs


class AlertRuleCreateView(LoginRequiredMixin, CreateView):
    model = AlertRule
    form_class = AlertRuleForm
    template_name = 'alerts/rule_form.html'
    success_url = reverse_lazy('alert_rules')

    def form_valid(self, form):
        tenant = self.request.tenant
        if not tenant and self.request.user.is_superuser:
            tenant = Tenant.objects.first()
            
        if not tenant:
            form.add_error(None, "Could not determine tenant for this rule. Please ensure your user is linked to a tenant.")
            return self.form_invalid(form)
            
        form.instance.tenant = tenant
        return super().form_valid(form)
