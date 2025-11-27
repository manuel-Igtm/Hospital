"""
URL configuration for security app.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BlockedIPViewSet,
    RateLimitViolationViewSet,
    RequestLogViewSet,
    SecurityDashboardView,
    SecurityEventViewSet,
)

router = DefaultRouter()
router.register(r"blocked-ips", BlockedIPViewSet, basename="blocked-ip")
router.register(r"request-logs", RequestLogViewSet, basename="request-log")
router.register(r"events", SecurityEventViewSet, basename="security-event")
router.register(r"rate-limits", RateLimitViolationViewSet, basename="rate-limit")

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/", SecurityDashboardView.as_view(), name="security-dashboard"),
]
