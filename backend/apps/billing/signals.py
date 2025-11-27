"""
Billing signals for invoice and payment events.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import InvoiceItem, Payment, PaymentStatus

logger = logging.getLogger(__name__)


@receiver(post_save, sender=InvoiceItem)
def recalculate_invoice_on_item_change(sender, instance, created, **kwargs):
    """Recalculate invoice totals when items change."""
    if instance.invoice_id:
        instance.invoice.recalculate()
        logger.debug(f"Recalculated invoice {instance.invoice.invoice_number} after item change")


@receiver(post_save, sender=Payment)
def log_payment_status_change(sender, instance, created, **kwargs):
    """Log payment status changes for audit."""
    if created:
        logger.info(
            f"New payment created: {instance.id} for invoice {instance.invoice.invoice_number}, "
            f"amount: {instance.amount}, method: {instance.payment_method}"
        )
    elif instance.status == PaymentStatus.COMPLETED:
        logger.info(
            f"Payment completed: {instance.id}, receipt: {instance.mpesa_receipt_number}, "
            f"amount: {instance.amount}"
        )
    elif instance.status == PaymentStatus.FAILED:
        logger.warning(
            f"Payment failed: {instance.id}, code: {instance.result_code}, "
            f"reason: {instance.result_description}"
        )
