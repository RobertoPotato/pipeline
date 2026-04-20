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
