from django.db import models
from core.models import Tenant

class ApiIngestionLog(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    source_system = models.CharField(max_length=100)
    endpoint = models.CharField(max_length=255)
    payload = models.JSONField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    status_code = models.IntegerField(default=200)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SegmentTelemetry(models.Model):
    segment = models.ForeignKey('assets.PipelineSegment', on_delete=models.CASCADE, related_name='telemetry')
    timestamp = models.DateTimeField(auto_now_add=True)
    flow_rate = models.FloatField(help_text="Current flow rate in BPH")
    daily_volume = models.FloatField(default=0.0, help_text="Total volume passed since last 24h")
    capacity_utilization = models.FloatField(help_text="Percentage of design capacity used")
    operating_pressure = models.FloatField(null=True, blank=True)
    operating_temperature = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
