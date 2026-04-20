from rest_framework import serializers
from telemetry.models import ApiIngestionLog


class ApiIngestionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiIngestionLog
        fields = ['id', 'tenant', 'source_system', 'endpoint', 'payload',
                  'ip_address', 'status_code', 'error_message', 'created_at']
        read_only_fields = ['id', 'created_at']
