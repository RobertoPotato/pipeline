from rest_framework import serializers
from core.models import Tenant, User


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'domain_name', 'primary_color', 'secondary_color',
                  'logo', 'favicon', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'role', 'tenant', 'tenant_name', 'is_active']
        read_only_fields = ['id']
