"""
Billing app configuration.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from django.apps import AppConfig


class BillingConfig(AppConfig):
    """Configuration for the billing app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.billing"
    verbose_name = "Billing & Payments"

    def ready(self):
        """Import signals when app is ready."""
        try:
            import apps.billing.signals  # noqa: F401
        except ImportError:
            pass
