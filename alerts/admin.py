from django.contrib import admin
from alerts.models import AlertRule, Notification


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'entity_type', 'metric',
                    'condition', 'threshold', 'is_active')
    list_filter = ('entity_type', 'is_active', 'tenant')
    search_fields = ('name', 'metric')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'tenant', 'rule', 'is_read', 'created_at')
    list_filter = ('is_read', 'tenant')
