"""
Security app configuration.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from django.apps import AppConfig


class SecurityConfig(AppConfig):
    """Configuration for the security app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.security"
    verbose_name = "Security & Audit"

    def ready(self):
        """Import signals when app is ready."""
        try:
            import apps.security.signals  # noqa: F401
        except ImportError:
            pass
