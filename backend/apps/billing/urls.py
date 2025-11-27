"""
URL configuration for billing app.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    InvoiceViewSet,
    MpesaCallbackView,
    MpesaQueryView,
    MpesaSTKPushView,
    PaymentViewSet,
    ServiceViewSet,
)

router = DefaultRouter()
router.register(r"services", ServiceViewSet, basename="service")
router.register(r"invoices", InvoiceViewSet, basename="invoice")
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    # ViewSet routes
    path("", include(router.urls)),
    # M-Pesa endpoints
    path("mpesa/stk-push/", MpesaSTKPushView.as_view(), name="mpesa-stk-push"),
    path("mpesa/callback/", MpesaCallbackView.as_view(), name="mpesa-callback"),
    path("mpesa/query/<uuid:payment_id>/", MpesaQueryView.as_view(), name="mpesa-query"),
]
