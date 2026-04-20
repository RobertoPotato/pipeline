"""
Template context processor for white-label branding.
Injects the current tenant's branding variables into every template.
"""


def tenant_branding(request):
    """Return tenant branding data for templates."""
    tenant = getattr(request, 'tenant', None)
    if tenant is None:
        return {
            'tenant_name': 'PipelineGuard',
            'primary_color': '#0f172a',
            'secondary_color': '#3b82f6',
            'tenant_logo': None,
            'tenant_favicon': None,
        }
    return {
        'tenant_name': tenant.name,
        'primary_color': tenant.primary_color,
        'secondary_color': tenant.secondary_color,
        'tenant_logo': tenant.logo.url if tenant.logo else None,
        'tenant_favicon': tenant.favicon.url if tenant.favicon else None,
        'tenant_background': tenant.login_background.url if tenant.login_background else None,
    }
