"""
Celery tasks for billing operations.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="apps.billing.tasks.check_overdue_invoices")
def check_overdue_invoices():
    """
    Check for overdue invoices and update their status.

    Runs hourly via Celery Beat.
    """
    from apps.billing.models import Invoice, InvoiceStatus

    today = timezone.now().date()

    # Find invoices that are past due date and still pending
    overdue = Invoice.objects.filter(
        status__in=[InvoiceStatus.PENDING, InvoiceStatus.PARTIALLY_PAID],
        due_date__lt=today,
    ).exclude(status=InvoiceStatus.OVERDUE)

    updated_count = 0
    for invoice in overdue:
        invoice.status = InvoiceStatus.OVERDUE
        invoice.save(update_fields=["status", "updated_at"])
        updated_count += 1
        logger.info(f"Marked invoice {invoice.invoice_number} as overdue")

    logger.info(f"Checked overdue invoices: {updated_count} marked as overdue")
    return {"updated": updated_count}


@shared_task(name="apps.billing.tasks.send_payment_reminder")
def send_payment_reminder(invoice_id: str):
    """
    Send payment reminder for an invoice.

    Args:
        invoice_id: UUID of the invoice
    """
    from apps.billing.models import Invoice

    try:
        invoice = Invoice.objects.select_related("patient").get(id=invoice_id)
    except Invoice.DoesNotExist:
        logger.error(f"Invoice {invoice_id} not found for reminder")
        return {"success": False, "error": "Invoice not found"}

    # Here you would integrate with SMS/Email service
    # For now, just log the reminder
    logger.info(
        f"Payment reminder for invoice {invoice.invoice_number}: "
        f"Patient {invoice.patient.full_name}, Amount: {invoice.balance_due}"
    )

    return {
        "success": True,
        "invoice_number": invoice.invoice_number,
        "patient": invoice.patient.full_name,
        "balance": str(invoice.balance_due),
    }


@shared_task(name="apps.billing.tasks.process_mpesa_timeout")
def process_mpesa_timeout(payment_id: str):
    """
    Process M-Pesa payment timeout.

    Called after STK push timeout period.
    """
    from apps.billing.models import Payment, PaymentStatus

    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        logger.error(f"Payment {payment_id} not found")
        return {"success": False, "error": "Payment not found"}

    # Only timeout if still processing
    if payment.status == PaymentStatus.PROCESSING:
        payment.status = PaymentStatus.TIMEOUT
        payment.result_description = "Payment request timed out"
        payment.save()
        logger.info(f"Payment {payment_id} marked as timeout")
        return {"success": True, "status": "timeout"}

    return {"success": True, "status": payment.status}


@shared_task(name="apps.billing.tasks.generate_daily_revenue_report")
def generate_daily_revenue_report():
    """
    Generate daily revenue report.

    Runs daily via Celery Beat.
    """
    from django.db.models import Count, Sum

    from apps.billing.models import Payment, PaymentStatus

    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # Get yesterday's revenue
    revenue = Payment.objects.filter(
        status=PaymentStatus.COMPLETED,
        created_at__date=yesterday,
    ).aggregate(
        total=Sum("amount"),
        count=Count("id"),
    )

    logger.info(
        f"Daily revenue report for {yesterday}: "
        f"Total: {revenue['total'] or 0} KES, "
        f"Transactions: {revenue['count']}"
    )

    return {
        "date": str(yesterday),
        "total_revenue": str(revenue["total"] or 0),
        "transaction_count": revenue["count"],
    }
