"""
Hospital Backend URL Configuration

API routes are prefixed with /api/v1/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for container orchestration."""
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def ping(request):
    """Simple ping endpoint."""
    return Response({'ping': 'pong'}, status=status.HTTP_200_OK)

urlpatterns = [
    # Admin
    path(settings.ADMIN_URL if hasattr(settings, 'ADMIN_URL') else 'admin/', admin.site.urls),
    
    # Health checks
    path('health/', health_check, name='health'),
    path('ping/', ping, name='ping'),
    
    # API v1
    path('api/v1/', include([
        # Auth
        path('auth/', include('apps.users.urls')),
        
        # Domain APIs
        path('patients/', include('apps.patients.urls')),
        path('appointments/', include('apps.appointments.urls')),
        path('encounters/', include('apps.encounters.urls')),
        path('orders/', include('apps.orders.urls')),
        path('labs/', include('apps.labs.urls')),
        path('medications/', include('apps.medications.urls')),
        path('billing/', include('apps.billing.urls')),
        path('insurance/', include('apps.insurance.urls')),
        path('audit/', include('apps.audit.urls')),
    ])),
    
    # API Documentation
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

# Customize admin site
admin.site.site_header = "Hospital Backend Administration"
admin.site.site_title = "Hospital Admin"
admin.site.index_title = "Welcome to Hospital Backend Administration"
