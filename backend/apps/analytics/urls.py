"""
URL configuration for analytics app.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from django.urls import path

from .views import (
    DashboardStatsView,
    LabAnalyticsView,
    OperationalMetricsView,
    PatientAnalyticsView,
    RevenueAnalyticsView,
)

urlpatterns = [
    path("dashboard/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("revenue/", RevenueAnalyticsView.as_view(), name="revenue-analytics"),
    path("patients/", PatientAnalyticsView.as_view(), name="patient-analytics"),
    path("lab/", LabAnalyticsView.as_view(), name="lab-analytics"),
    path("operational/", OperationalMetricsView.as_view(), name="operational-metrics"),
]
