"""
Permissions for tenant-scoped access control.
"""
from rest_framework import permissions


class IsTenantUser(permissions.BasePermission):
    """Only allow access if the user belongs to a tenant."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request, 'tenant', None))


class IsTenantAdmin(permissions.BasePermission):
    """Only Tenant Admins or Super Admins."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ('TENANT_ADMIN', 'SUPER_ADMIN')


class IsSuperAdmin(permissions.BasePermission):
    """Only Super Admins."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'SUPER_ADMIN'


class TenantQuerysetMixin:
    """
    Mixin for viewsets that automatically filters querysets by the
    current request's tenant. Ensures complete data isolation.
    """
    tenant_field = 'tenant'  # override in subclass if FK name differs

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
            return qs.filter(**{self.tenant_field: tenant})
        if self.request.user.role == 'SUPER_ADMIN':
            return qs
        return qs.none()
