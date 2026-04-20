from django.db import models
from assets.models import PipelineSegment, ProductType, Depot
from core.models import Tenant

class Batch(models.Model):
    """Represents a specific volume of product currently moving through a segment."""
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled')
    ]
    
    batch_identifier = models.CharField(max_length=100, unique=True)
    segment = models.ForeignKey(PipelineSegment, on_delete=models.CASCADE, related_name='active_batches')
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    
    total_volume = models.FloatField()
    origin_depot = models.ForeignKey(Depot, on_delete=models.SET_NULL, null=True, related_name='originated_batches')
    destination_depot = models.ForeignKey(Depot, on_delete=models.SET_NULL, null=True, related_name='destined_batches')
    
    start_time = models.DateTimeField(null=True, blank=True)
    estimated_arrival_time = models.DateTimeField(null=True, blank=True)
    
    # Live Tracking
    current_position_km = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')

    @property
    def progress_percentage(self):
        if self.segment.length_km == 0: return 0
        return min(100.0, (self.current_position_km / self.segment.length_km) * 100)

    @property
    def total_volume_passed(self):
        # Prefer the latest reported accumulated volume
        latest = self.history.last()
        if latest and latest.accumulated_volume:
            return latest.accumulated_volume
        return 0.0

    def __str__(self):
        return f"Batch {self.batch_identifier} ({self.product_type.name})"

class BatchHistory(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='history')
    recorded_at = models.DateTimeField(auto_now_add=True)
    position_km = models.FloatField()
    flow_rate = models.FloatField(null=True, blank=True, help_text="Flow rate in barrels per hour")
    accumulated_volume = models.FloatField(default=0.0, help_text="Total volume passed since batch start")
    temperature = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    interface_mixing_volume = models.FloatField(default=0.0, help_text="Estimated mixture with adjacent batch")

class VesselDischarge(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('BERTHED', 'Berthed'),
        ('DISCHARGING', 'Discharging'),
        ('COMPLETED', 'Completed')
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    vessel_name = models.CharField(max_length=200)
    terminal_depot = models.ForeignKey(Depot, on_delete=models.CASCADE, related_name='vessel_discharges')
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    
    total_volume = models.FloatField()
    discharged_volume = models.FloatField(default=0.0)
    
    start_time = models.DateTimeField(null=True, blank=True)
    estimated_completion_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    @property
    def remaining_volume(self):
        return max(0.0, self.total_volume - self.discharged_volume)
