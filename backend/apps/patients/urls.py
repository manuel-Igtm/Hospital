"""
URL configuration for patients app.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import PatientViewSet

router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patient")

urlpatterns = [
    path("", include(router.urls)),
]
