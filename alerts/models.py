from django.db import models
from core.models import Tenant

class AlertRule(models.Model):
    ENTITY_CHOICES = [('TANK', 'Tank'), ('PIPELINE', 'Pipeline Segment'), ('BATCH', 'Batch'), ('VESSEL', 'Vessel')]
    CONDITION_CHOICES = [('>', 'Greater Than'), ('<', 'Less Than'), ('==', 'Equals'), ('!=', 'Not Equals')]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='alert_rules')
    name = models.CharField(max_length=150)
    
    entity_type = models.CharField(max_length=20, choices=ENTITY_CHOICES)
    # Generic linkage to the exact entity ID (can be 0/null to apply to all)
    entity_id = models.IntegerField(null=True, blank=True, help_text="ID of the specific Tank, Pipeline, etc.")
    
    metric = models.CharField(max_length=50, help_text="e.g., ullage, pressure, status, interface_volume")
    condition = models.CharField(max_length=5, choices=CONDITION_CHOICES)
    threshold = models.FloatField()
    
    message_template = models.CharField(max_length=255, help_text="Use {entity} and {value} in string")
    is_active = models.BooleanField(default=True)

class Notification(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    rule = models.ForeignKey(AlertRule, on_delete=models.SET_NULL, null=True, blank=True)
    
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
