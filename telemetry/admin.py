from django.contrib import admin
from telemetry.models import ApiIngestionLog


@admin.register(ApiIngestionLog)
class ApiIngestionLogAdmin(admin.ModelAdmin):
    list_display = ('source_system', 'tenant', 'endpoint', 'status_code',
                    'ip_address', 'created_at')
    list_filter = ('source_system', 'status_code', 'tenant')
    search_fields = ('endpoint', 'source_system')
    readonly_fields = ('payload',)
