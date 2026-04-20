import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


def generate_api_key():
    return uuid.uuid4().hex


class Tenant(models.Model):
    """
    White Labeling tenant. Every record in the system will tie back to a tenant
    to ensure data isolation for different Oil Marketing Companies (OMCs).
    """
    name = models.CharField(max_length=255, unique=True)
    domain_name = models.CharField(max_length=255, unique=True, help_text="e.g., omc1.pipelineguard.com")

    # API access
    api_key = models.CharField(max_length=64, unique=True, default=generate_api_key, editable=False)

    # Branding
    primary_color = models.CharField(max_length=20, default="#0f172a")
    secondary_color = models.CharField(max_length=20, default="#3b82f6")
    logo = models.ImageField(upload_to="tenant_logos/", null=True, blank=True)
    favicon = models.ImageField(upload_to="tenant_favicons/", null=True, blank=True)
    login_background = models.ImageField(upload_to="tenant_backgrounds/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = (
        ('SUPER_ADMIN', 'Super Admin'),
        ('TENANT_ADMIN', 'Tenant Admin'),
        ('OPERATOR', 'Operator'),
        ('VIEWER', 'Viewer'),
    )
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='VIEWER')

    def __str__(self):
        return f"{self.username} - {self.role}"
