"""
Analytics app configuration.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """Configuration for the analytics app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analytics"
    verbose_name = "Analytics & Reporting"
