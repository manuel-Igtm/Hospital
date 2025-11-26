"""Patients app configuration."""

from django.apps import AppConfig


class PatientsConfig(AppConfig):
    """Configuration for the patients application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.patients"
    verbose_name = "Patient Management"

    def ready(self):
        """Import signal handlers when app is ready."""
        try:
            import apps.patients.signals  # noqa: F401
        except ImportError:
            pass
