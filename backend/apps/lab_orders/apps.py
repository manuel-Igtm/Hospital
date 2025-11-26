"""Lab Orders app configuration."""

from django.apps import AppConfig


class LabOrdersConfig(AppConfig):
    """Configuration for the lab_orders application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.lab_orders'
    verbose_name = 'Laboratory Orders'
