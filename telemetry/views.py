from rest_framework import viewsets, permissions
from telemetry.models import ApiIngestionLog
from telemetry.serializers import ApiIngestionLogSerializer
from core.permissions import IsTenantAdmin, TenantQuerysetMixin


class ApiIngestionLogViewSet(TenantQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    """Read-only audit trail of all data ingestion calls."""
    queryset = ApiIngestionLog.objects.all().order_by('-created_at')
    serializer_class = ApiIngestionLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantAdmin]
    filterset_fields = ['source_system', 'status_code']
    search_fields = ['endpoint', 'source_system']
    ordering_fields = ['created_at']
