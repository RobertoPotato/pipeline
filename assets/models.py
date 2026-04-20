from django.db import models
from core.models import Tenant

class ProductType(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='product_types')
    name = models.CharField(max_length=50) # e.g., PMS, AGO, JET A1
    color_code = models.CharField(max_length=20, default="#cccccc") # e.g., yellow, red, blue
    specific_gravity = models.FloatField(null=True, blank=True)
    max_interface_mixing_tolerance = models.FloatField(default=0.0, help_text="Acceptable mixture volume in bbls/liters")

    class Meta:
        unique_together = ('tenant', 'name')

    def __str__(self):
        return self.name

class Depot(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='depots')
    name = models.CharField(max_length=150)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class Tank(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('MAINTENANCE', 'Maintenance'),
        ('OUT_OF_SERVICE', 'Out of Service')
    ]
    
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE, related_name='tanks')
    name = models.CharField(max_length=100)
    product_type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True, related_name='tanks')
    max_capacity = models.FloatField(help_text="Maximum roof capacity")
    safe_fill_capacity = models.FloatField(help_text="Operational safe fill limit")
    
    # Telemetry data (updated frequently)
    current_volume = models.FloatField(default=0.0)
    current_temperature = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def ullage(self):
        """Available empty space up to safe fill capacity."""
        return max(0.0, self.safe_fill_capacity - self.current_volume)
        
    @property
    def fill_percentage(self):
        if self.safe_fill_capacity == 0: return 0
        return (self.current_volume / self.safe_fill_capacity) * 100

    def __str__(self):
        return f"{self.depot.name} - {self.name}"

class PipelineSegment(models.Model):
    STATUS_CHOICES = [
        ('FLOWING', 'Flowing'),
        ('STATIC', 'Static'),
        ('OFFLINE', 'Offline'),
        ('PIGGING', 'Pigging'),
        ('MAINTENANCE', 'Maintenance')
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='pipeline_segments')
    name = models.CharField(max_length=150)
    origin = models.ForeignKey(Depot, on_delete=models.SET_NULL, null=True, related_name='segments_originating')
    destination = models.ForeignKey(Depot, on_delete=models.SET_NULL, null=True, related_name='segments_terminating')
    
    length_km = models.FloatField()
    diameter_inches = models.FloatField()
    volume_capacity = models.FloatField(help_text="Line fill capacity")
    
    # Telemetry updates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OFFLINE')
    current_flow_rate = models.FloatField(default=0.0)
    current_pressure = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    # GeoJSON representation for Leaflet UI mapping
    geojson_path = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name
