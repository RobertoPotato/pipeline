"""
Custom DRF authentication backend for API-key based access.
External SCADA systems authenticate with an API key scoped to a tenant.
"""
from rest_framework import authentication, exceptions

from core.models import Tenant, User


class TenantApiKeyAuthentication(authentication.BaseAuthentication):
    """
    Authenticate via X-API-KEY header.
    The API key is stored on the Tenant model (we add the field via migration).
    For MVP we use a simple token stored on Tenant.  Production should use
    hashed keys or a dedicated ApiKey model.
    """

    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None  # Let other backends try

        try:
            tenant = Tenant.objects.get(api_key=api_key)
        except Tenant.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API key.')

        # Return a synthetic "service account" user for this tenant
        service_user, _ = User.objects.get_or_create(
            username=f'api_service_{tenant.pk}',
            defaults={
                'tenant': tenant,
                'role': 'OPERATOR',
                'is_active': True,
            },
        )
        service_user.tenant = tenant  # ensure always current
        request.tenant = tenant
        return (service_user, tenant)
