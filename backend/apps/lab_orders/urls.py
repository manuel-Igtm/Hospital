"""
URL configuration for lab_orders app.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import LabOrderViewSet, LabResultViewSet, TestTypeViewSet

router = DefaultRouter()
router.register(r"test-types", TestTypeViewSet, basename="test-type")
router.register(r"orders", LabOrderViewSet, basename="lab-order")
router.register(r"results", LabResultViewSet, basename="lab-result")

urlpatterns = [
    path("", include(router.urls)),
]
