"""
Hospital Backend URL Configuration

API routes are prefixed with /api/v1/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for container orchestration."""
    return Response({"status": "healthy"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def ping(request):
    """Simple ping endpoint."""
    return Response({"ping": "pong"}, status=status.HTTP_200_OK)


urlpatterns = [
    # Admin
    path(settings.ADMIN_URL if hasattr(settings, "ADMIN_URL") else "admin/", admin.site.urls),
    # Health checks
    path("health/", health_check, name="health"),
    path("ping/", ping, name="ping"),
    # API v1
    path(
        "api/v1/",
        include(
            [
                # Auth & Users
                path("", include("apps.users.urls")),
                # Patients
                path("", include("apps.patients.urls")),
                # Lab Orders
                path("lab/", include("apps.lab_orders.urls")),
                # Billing & Payments
                path("billing/", include("apps.billing.urls")),
                # Analytics
                path("analytics/", include("apps.analytics.urls")),
                # Security
                path("security/", include("apps.security.urls")),
            ]
        ),
    ),
    # API Documentation
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug toolbar
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar  # type: ignore[import-not-found]

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

# Customize admin site
admin.site.site_header = "Hospital Backend Administration"
admin.site.site_title = "Hospital Admin"
admin.site.index_title = "Welcome to Hospital Backend Administration"
