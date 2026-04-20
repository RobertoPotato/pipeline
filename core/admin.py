from django.contrib import admin
from core.models import Tenant, User


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain_name', 'api_key', 'created_at')
    search_fields = ('name', 'domain_name')
    readonly_fields = ('api_key', 'created_at', 'updated_at')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'tenant', 'role', 'is_active')
    list_filter = ('role', 'tenant', 'is_active')
    search_fields = ('username', 'email')
