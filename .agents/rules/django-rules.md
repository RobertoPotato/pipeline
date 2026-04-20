---
trigger: always_on
---

You are an expert in the Django web framework for Python.

Key Principles:
- Follow the 'Batteries Included' philosophy
- Don't Repeat Yourself (DRY)
- Explicit is better than implicit
- Fat Models, Thin Views
- Secure by default

Models & ORM:
- Use models to define database schema
- Use migrations for schema changes (makemigrations, migrate)
- Optimize queries with select_related (FK) and prefetch_related (M2M)
- Use Managers and QuerySets for business logic
- Avoid N+1 query problems

Views & URLs:
- Use Function-Based Views (FBVs)
- Name your URL patterns for reverse lookups
- Keep views focused on request/response logic

Django REST Framework (DRF):
- Use Serializers for data conversion and validation
- Use ViewSets and Routers for standard APIs
- Use Generic Views for customization
- Implement proper permissions and authentication
- Use Throttling for rate limiting

Forms & Admin:
- Use ModelForms to generate forms from models
- Customize the Admin interface (ModelAdmin)
- Use inline formsets in Admin
- Validate data in clean() methods

Security:
- Protect against CSRF (enabled by default)
- Use Django's authentication system
- Sanitize user input (handled by templates/ORM)
- Set SECURE_SSL_REDIRECT in production
- Use environment variables for secrets

Best Practices:
- Use a custom User model from the start
- Use django allauth by default with email/password authentication and OTP
- Use Celery for background tasks
- Write tests (TestCase, APITestCase)
- Use Django Debug Toolbar for profiling

UI/UX:
- Use Tailwind Css for styling
- Apply modern styling with dark/light mode
- UI should be responsive
- Use HTMX for responsive data fetching
- Use django cotton to set up reusable components
- Use django plotly dash for any graphing/charting needs

MAP Features:
- Use leaflet maps where maps are used