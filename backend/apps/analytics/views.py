"""
Analytics views for dashboard and reporting.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.billing.models import Invoice, InvoiceStatus, Payment, PaymentStatus
from apps.lab_orders.models import LabOrder
from apps.patients.models import Patient
from apps.users.models import User, UserRole


class DashboardStatsView(APIView):
    """
    Get dashboard statistics overview.

    GET /api/v1/analytics/dashboard/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return dashboard statistics."""
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        start_of_week = today - timedelta(days=today.weekday())

        # Patient statistics
        total_patients = Patient.objects.filter(is_active=True).count()
        new_patients_month = Patient.objects.filter(
            created_at__date__gte=start_of_month
        ).count()
        new_patients_week = Patient.objects.filter(
            created_at__date__gte=start_of_week
        ).count()

        # Lab order statistics
        total_lab_orders = LabOrder.objects.count()
        pending_lab_orders = LabOrder.objects.filter(status="PENDING").count()
        completed_lab_orders_today = LabOrder.objects.filter(
            status__in=["RESULTED", "REVIEWED"],
            updated_at__date=today,
        ).count()

        # Revenue statistics
        revenue_month = (
            Payment.objects.filter(
                status=PaymentStatus.COMPLETED,
                created_at__date__gte=start_of_month,
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        revenue_today = (
            Payment.objects.filter(
                status=PaymentStatus.COMPLETED,
                created_at__date=today,
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        # Invoice statistics
        pending_invoices = Invoice.objects.filter(
            status__in=[InvoiceStatus.PENDING, InvoiceStatus.PARTIALLY_PAID]
        ).count()
        overdue_invoices = Invoice.objects.filter(
            status__in=[InvoiceStatus.PENDING, InvoiceStatus.PARTIALLY_PAID],
            due_date__lt=today,
        ).count()
        total_outstanding = (
            Invoice.objects.filter(
                status__in=[InvoiceStatus.PENDING, InvoiceStatus.PARTIALLY_PAID]
            ).aggregate(total=Sum("balance_due"))["total"]
            or Decimal("0.00")
        )

        # Staff statistics
        total_staff = User.objects.filter(is_active=True).exclude(role=UserRole.ADMIN).count()
        doctors = User.objects.filter(is_active=True, role=UserRole.DOCTOR).count()
        nurses = User.objects.filter(is_active=True, role=UserRole.NURSE).count()
        lab_techs = User.objects.filter(is_active=True, role=UserRole.LAB_TECH).count()

        return Response(
            {
                "patients": {
                    "total": total_patients,
                    "new_this_month": new_patients_month,
                    "new_this_week": new_patients_week,
                },
                "lab_orders": {
                    "total": total_lab_orders,
                    "pending": pending_lab_orders,
                    "completed_today": completed_lab_orders_today,
                },
                "revenue": {
                    "today": str(revenue_today),
                    "this_month": str(revenue_month),
                    "currency": "KES",
                },
                "invoices": {
                    "pending": pending_invoices,
                    "overdue": overdue_invoices,
                    "total_outstanding": str(total_outstanding),
                },
                "staff": {
                    "total": total_staff,
                    "doctors": doctors,
                    "nurses": nurses,
                    "lab_technicians": lab_techs,
                },
                "generated_at": timezone.now().isoformat(),
            }
        )


class RevenueAnalyticsView(APIView):
    """
    Get revenue analytics and trends.

    GET /api/v1/analytics/revenue/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return revenue analytics."""
        # Get date range from query params
        days = int(request.query_params.get("days", 30))
        start_date = timezone.now().date() - timedelta(days=days)

        # Daily revenue trend
        daily_revenue = (
            Payment.objects.filter(
                status=PaymentStatus.COMPLETED,
                created_at__date__gte=start_date,
            )
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("date")
        )

        # Revenue by payment method
        revenue_by_method = (
            Payment.objects.filter(
                status=PaymentStatus.COMPLETED,
                created_at__date__gte=start_date,
            )
            .values("payment_method")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
        )

        # Monthly revenue (last 12 months)
        twelve_months_ago = timezone.now().date() - timedelta(days=365)
        monthly_revenue = (
            Payment.objects.filter(
                status=PaymentStatus.COMPLETED,
                created_at__date__gte=twelve_months_ago,
            )
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("month")
        )

        # Top services by revenue
        from apps.billing.models import InvoiceItem

        top_services = (
            InvoiceItem.objects.filter(
                invoice__status=InvoiceStatus.PAID,
                invoice__created_at__date__gte=start_date,
            )
            .values("service__name", "service__category")
            .annotate(total_revenue=Sum("total_price"), orders=Count("id"))
            .order_by("-total_revenue")[:10]
        )

        return Response(
            {
                "period_days": days,
                "daily_trend": [
                    {
                        "date": item["date"].isoformat(),
                        "revenue": str(item["total"]),
                        "transactions": item["count"],
                    }
                    for item in daily_revenue
                ],
                "by_payment_method": [
                    {
                        "method": item["payment_method"],
                        "revenue": str(item["total"]),
                        "transactions": item["count"],
                    }
                    for item in revenue_by_method
                ],
                "monthly_trend": [
                    {
                        "month": item["month"].strftime("%Y-%m"),
                        "revenue": str(item["total"]),
                        "transactions": item["count"],
                    }
                    for item in monthly_revenue
                ],
                "top_services": [
                    {
                        "service": item["service__name"],
                        "category": item["service__category"],
                        "revenue": str(item["total_revenue"]),
                        "orders": item["orders"],
                    }
                    for item in top_services
                ],
            }
        )


class PatientAnalyticsView(APIView):
    """
    Get patient analytics and demographics.

    GET /api/v1/analytics/patients/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return patient analytics."""
        days = int(request.query_params.get("days", 30))
        start_date = timezone.now().date() - timedelta(days=days)

        # New patients trend
        new_patients_trend = (
            Patient.objects.filter(created_at__date__gte=start_date)
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        # Gender distribution
        gender_distribution = (
            Patient.objects.filter(is_active=True)
            .values("gender")
            .annotate(count=Count("id"))
        )

        # Blood type distribution
        blood_type_distribution = (
            Patient.objects.filter(is_active=True)
            .values("blood_type")
            .annotate(count=Count("id"))
        )

        # Age distribution
        today = timezone.now().date()
        age_ranges = {
            "0-17": 0,
            "18-30": 0,
            "31-45": 0,
            "46-60": 0,
            "61+": 0,
        }

        for patient in Patient.objects.filter(is_active=True).values("date_of_birth"):
            dob = patient["date_of_birth"]
            age = (
                today.year
                - dob.year
                - ((today.month, today.day) < (dob.month, dob.day))
            )
            if age < 18:
                age_ranges["0-17"] += 1
            elif age <= 30:
                age_ranges["18-30"] += 1
            elif age <= 45:
                age_ranges["31-45"] += 1
            elif age <= 60:
                age_ranges["46-60"] += 1
            else:
                age_ranges["61+"] += 1

        return Response(
            {
                "period_days": days,
                "total_active": Patient.objects.filter(is_active=True).count(),
                "new_patients_trend": [
                    {"date": item["date"].isoformat(), "count": item["count"]}
                    for item in new_patients_trend
                ],
                "gender_distribution": {
                    item["gender"]: item["count"] for item in gender_distribution
                },
                "blood_type_distribution": {
                    item["blood_type"]: item["count"]
                    for item in blood_type_distribution
                },
                "age_distribution": age_ranges,
            }
        )


class LabAnalyticsView(APIView):
    """
    Get laboratory analytics.

    GET /api/v1/analytics/lab/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return lab analytics."""
        days = int(request.query_params.get("days", 30))
        start_date = timezone.now().date() - timedelta(days=days)

        # Orders by status
        orders_by_status = (
            LabOrder.objects.filter(ordered_at__date__gte=start_date)
            .values("status")
            .annotate(count=Count("id"))
        )

        # Orders trend
        orders_trend = (
            LabOrder.objects.filter(ordered_at__date__gte=start_date)
            .annotate(date=TruncDate("ordered_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        # Top test types
        top_tests = (
            LabOrder.objects.filter(ordered_at__date__gte=start_date)
            .values("test_type__name", "test_type__code")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        # Average turnaround time (for completed orders)
        completed_orders = LabOrder.objects.filter(
            status__in=["RESULTED", "REVIEWED"],
            ordered_at__date__gte=start_date,
        )

        total_turnaround = timedelta()
        completed_count = 0
        for order in completed_orders:
            if order.updated_at and order.ordered_at:
                total_turnaround += order.updated_at - order.ordered_at
                completed_count += 1

        avg_turnaround_hours = (
            total_turnaround.total_seconds() / 3600 / completed_count
            if completed_count > 0
            else 0
        )

        return Response(
            {
                "period_days": days,
                "total_orders": LabOrder.objects.filter(
                    ordered_at__date__gte=start_date
                ).count(),
                "orders_by_status": {
                    item["status"]: item["count"] for item in orders_by_status
                },
                "orders_trend": [
                    {"date": item["date"].isoformat(), "count": item["count"]}
                    for item in orders_trend
                ],
                "top_test_types": [
                    {
                        "name": item["test_type__name"],
                        "code": item["test_type__code"],
                        "count": item["count"],
                    }
                    for item in top_tests
                ],
                "avg_turnaround_hours": round(avg_turnaround_hours, 2),
            }
        )


class OperationalMetricsView(APIView):
    """
    Get operational metrics for the hospital.

    GET /api/v1/analytics/operational/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return operational metrics."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)

        # Today's activity
        today_patients = Patient.objects.filter(created_at__date=today).count()
        today_lab_orders = LabOrder.objects.filter(ordered_at__date=today).count()
        today_invoices = Invoice.objects.filter(created_at__date=today).count()
        today_payments = Payment.objects.filter(
            status=PaymentStatus.COMPLETED, created_at__date=today
        ).count()

        # Comparison with yesterday
        yesterday_patients = Patient.objects.filter(created_at__date=yesterday).count()
        yesterday_lab_orders = LabOrder.objects.filter(
            ordered_at__date=yesterday
        ).count()
        yesterday_invoices = Invoice.objects.filter(created_at__date=yesterday).count()
        yesterday_payments = Payment.objects.filter(
            status=PaymentStatus.COMPLETED, created_at__date=yesterday
        ).count()

        def calc_change(today_val, yesterday_val):
            if yesterday_val == 0:
                return 100 if today_val > 0 else 0
            return round((today_val - yesterday_val) / yesterday_val * 100, 1)

        # Payment success rate
        total_payment_attempts = Payment.objects.filter(
            created_at__date__gte=last_month
        ).count()
        successful_payments = Payment.objects.filter(
            status=PaymentStatus.COMPLETED, created_at__date__gte=last_month
        ).count()
        payment_success_rate = (
            successful_payments / total_payment_attempts * 100
            if total_payment_attempts > 0
            else 0
        )

        # Collection rate
        total_invoiced = (
            Invoice.objects.filter(created_at__date__gte=last_month).aggregate(
                total=Sum("total_amount")
            )["total"]
            or Decimal("0.00")
        )
        total_collected = (
            Payment.objects.filter(
                status=PaymentStatus.COMPLETED, created_at__date__gte=last_month
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )
        collection_rate = (
            float(total_collected) / float(total_invoiced) * 100
            if total_invoiced > 0
            else 0
        )

        return Response(
            {
                "today": {
                    "new_patients": today_patients,
                    "lab_orders": today_lab_orders,
                    "invoices_created": today_invoices,
                    "payments_received": today_payments,
                },
                "changes_from_yesterday": {
                    "patients": calc_change(today_patients, yesterday_patients),
                    "lab_orders": calc_change(today_lab_orders, yesterday_lab_orders),
                    "invoices": calc_change(today_invoices, yesterday_invoices),
                    "payments": calc_change(today_payments, yesterday_payments),
                },
                "last_30_days": {
                    "payment_success_rate": round(payment_success_rate, 1),
                    "collection_rate": round(collection_rate, 1),
                    "total_invoiced": str(total_invoiced),
                    "total_collected": str(total_collected),
                },
                "generated_at": timezone.now().isoformat(),
            }
        )
