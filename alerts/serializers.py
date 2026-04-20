from rest_framework import serializers
from alerts.models import AlertRule, Notification


class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = ['id', 'tenant', 'name', 'entity_type', 'entity_id',
                  'metric', 'condition', 'threshold',
                  'message_template', 'is_active']
        read_only_fields = ['id']


class NotificationSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source='rule.name', read_only=True, default=None)

    class Meta:
        model = Notification
        fields = ['id', 'tenant', 'rule', 'rule_name', 'message',
                  'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']
