"""
Tenant middleware — resolves the current tenant from the request
and attaches it to request.tenant for all downstream access.
"""
from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
    """
    Attach the tenant to each request based on the logged-in user's tenant FK.
    For API key auth the tenant is set by TenantApiKeyAuthentication.
    """

    def process_request(self, request):
        request.tenant = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.tenant = getattr(request.user, 'tenant', None)
