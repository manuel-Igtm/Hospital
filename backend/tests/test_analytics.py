"""
Tests for analytics app - dashboards and reports.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone

from rest_framework import status

import pytest

from apps.billing.models import Invoice, InvoiceItem, InvoiceStatus, Payment, PaymentMethod, PaymentStatus, Service
from apps.lab_orders.models import LabOrder, TestType
from apps.patients.models import Patient


@pytest.fixture
def setup_analytics_data(db, admin_user, doctor_user):
    """Create test data for analytics."""
    # Create patients
    patients = []
    for i in range(5):
        patient = Patient.objects.create(
            first_name=f"Patient{i}",
            last_name=f"Test{i}",
            date_of_birth=date(1990 - i * 5, 1, 1),
            gender="M" if i % 2 == 0 else "F",
        )
        patients.append(patient)

    # Create services
    service = Service.objects.create(
        code="LAB001",
        name="Blood Test",
        category="LABORATORY",
        unit_price=Decimal("500.00"),
    )

    # Create invoices and payments
    for patient in patients[:3]:
        invoice = Invoice.objects.create(
            patient=patient,
            due_date=date.today() + timedelta(days=30),
            status=InvoiceStatus.PAID,
            created_by=admin_user,
        )
        InvoiceItem.objects.create(
            invoice=invoice,
            service=service,
            quantity=1,
            unit_price=service.unit_price,
        )
        invoice.recalculate()

        Payment.objects.create(
            invoice=invoice,
            payment_method=PaymentMethod.MPESA,
            amount=Decimal("500.00"),
            status=PaymentStatus.COMPLETED,
        )

    # Create test types for lab orders
    test_type = TestType.objects.create(
        code="CBC",
        name="Complete Blood Count",
        category="HEMATOLOGY",
    )

    # Create lab orders - LabOrder uses test_type directly
    for patient in patients[:2]:
        LabOrder.objects.create(
            patient=patient,
            ordering_provider=doctor_user,
            test_type=test_type,
            status="RESULTED",
        )

    return {
        "patients": patients,
        "service": service,
    }


class TestDashboardStats:
    """Tests for dashboard statistics endpoint."""

    def test_get_dashboard_stats(self, authenticated_admin_client, setup_analytics_data):
        """Test getting dashboard statistics."""
        url = reverse("dashboard-stats")
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "patients" in response.data
        assert "lab_orders" in response.data
        assert "revenue" in response.data
        assert "invoices" in response.data
        assert "staff" in response.data

    def test_dashboard_patient_stats(self, authenticated_admin_client, setup_analytics_data):
        """Test patient statistics in dashboard."""
        url = reverse("dashboard-stats")
        response = authenticated_admin_client.get(url)

        assert response.data["patients"]["total"] >= 5

    def test_dashboard_requires_auth(self, db, api_client):
        """Test dashboard requires authentication."""
        url = reverse("dashboard-stats")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRevenueAnalytics:
    """Tests for revenue analytics endpoint."""

    def test_get_revenue_analytics(self, authenticated_admin_client, setup_analytics_data):
        """Test getting revenue analytics."""
        url = reverse("revenue-analytics")
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "daily_trend" in response.data
        assert "by_payment_method" in response.data
        assert "monthly_trend" in response.data
        assert "top_services" in response.data

    def test_revenue_with_custom_days(self, authenticated_admin_client, setup_analytics_data):
        """Test revenue analytics with custom day range."""
        url = reverse("revenue-analytics")
        response = authenticated_admin_client.get(url, {"days": 7})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["period_days"] == 7

    def test_revenue_by_payment_method(self, authenticated_admin_client, setup_analytics_data):
        """Test revenue breakdown by payment method."""
        url = reverse("revenue-analytics")
        response = authenticated_admin_client.get(url)

        # Should have M-Pesa payments from setup data
        methods = {item["method"] for item in response.data["by_payment_method"]}
        assert PaymentMethod.MPESA in methods


class TestPatientAnalytics:
    """Tests for patient analytics endpoint."""

    def test_get_patient_analytics(self, authenticated_admin_client, setup_analytics_data):
        """Test getting patient analytics."""
        url = reverse("patient-analytics")
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "total_active" in response.data
        assert "new_patients_trend" in response.data
        assert "gender_distribution" in response.data
        assert "blood_type_distribution" in response.data
        assert "age_distribution" in response.data

    def test_patient_gender_distribution(self, authenticated_admin_client, setup_analytics_data):
        """Test patient gender distribution."""
        url = reverse("patient-analytics")
        response = authenticated_admin_client.get(url)

        gender_dist = response.data["gender_distribution"]
        assert "M" in gender_dist or "F" in gender_dist

    def test_patient_age_distribution(self, authenticated_admin_client, setup_analytics_data):
        """Test patient age distribution."""
        url = reverse("patient-analytics")
        response = authenticated_admin_client.get(url)

        age_dist = response.data["age_distribution"]
        assert "0-17" in age_dist
        assert "18-30" in age_dist
        assert "31-45" in age_dist
        assert "46-60" in age_dist
        assert "61+" in age_dist


class TestLabAnalytics:
    """Tests for laboratory analytics endpoint."""

    def test_get_lab_analytics(self, authenticated_admin_client, setup_analytics_data):
        """Test getting lab analytics."""
        url = reverse("lab-analytics")
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "total_orders" in response.data
        assert "orders_by_status" in response.data
        assert "orders_trend" in response.data
        assert "top_test_types" in response.data
        assert "avg_turnaround_hours" in response.data

    def test_lab_orders_by_status(self, authenticated_admin_client, setup_analytics_data):
        """Test lab orders by status breakdown."""
        url = reverse("lab-analytics")
        response = authenticated_admin_client.get(url)

        # Should have resulted orders from setup
        status_counts = response.data["orders_by_status"]
        assert "RESULTED" in status_counts


class TestOperationalMetrics:
    """Tests for operational metrics endpoint."""

    def test_get_operational_metrics(self, authenticated_admin_client, setup_analytics_data):
        """Test getting operational metrics."""
        url = reverse("operational-metrics")
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "today" in response.data
        assert "changes_from_yesterday" in response.data
        assert "last_30_days" in response.data

    def test_operational_today_stats(self, authenticated_admin_client, setup_analytics_data):
        """Test today's operational statistics."""
        url = reverse("operational-metrics")
        response = authenticated_admin_client.get(url)

        today = response.data["today"]
        assert "new_patients" in today
        assert "lab_orders" in today
        assert "invoices_created" in today
        assert "payments_received" in today

    def test_operational_collection_rate(self, authenticated_admin_client, setup_analytics_data):
        """Test collection rate calculation."""
        url = reverse("operational-metrics")
        response = authenticated_admin_client.get(url)

        last_30 = response.data["last_30_days"]
        assert "collection_rate" in last_30
        assert "payment_success_rate" in last_30
