"""
Billing models for invoices and M-Pesa payments.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class InvoiceStatus(models.TextChoices):
    """Invoice status choices."""

    DRAFT = "DRAFT", "Draft"
    PENDING = "PENDING", "Pending Payment"
    PARTIALLY_PAID = "PARTIAL", "Partially Paid"
    PAID = "PAID", "Paid"
    OVERDUE = "OVERDUE", "Overdue"
    CANCELLED = "CANCELLED", "Cancelled"
    REFUNDED = "REFUNDED", "Refunded"


class PaymentStatus(models.TextChoices):
    """Payment status choices."""

    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"
    REFUNDED = "REFUNDED", "Refunded"
    TIMEOUT = "TIMEOUT", "Timeout"


class PaymentMethod(models.TextChoices):
    """Payment method choices."""

    MPESA = "MPESA", "M-Pesa"
    CASH = "CASH", "Cash"
    CARD = "CARD", "Credit/Debit Card"
    INSURANCE = "INSURANCE", "Insurance"
    BANK_TRANSFER = "BANK", "Bank Transfer"


class ServiceCategory(models.TextChoices):
    """Hospital service categories."""

    CONSULTATION = "CONSULTATION", "Consultation"
    LABORATORY = "LABORATORY", "Laboratory Tests"
    PHARMACY = "PHARMACY", "Pharmacy"
    RADIOLOGY = "RADIOLOGY", "Radiology"
    PROCEDURE = "PROCEDURE", "Medical Procedure"
    ADMISSION = "ADMISSION", "Hospital Admission"
    SURGERY = "SURGERY", "Surgery"
    EMERGENCY = "EMERGENCY", "Emergency Services"
    OTHER = "OTHER", "Other Services"


class Service(models.Model):
    """
    Hospital services that can be billed.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, db_index=True, help_text="Service code")
    name = models.CharField(max_length=200, help_text="Service name")
    description = models.TextField(blank=True, help_text="Service description")
    category = models.CharField(
        max_length=20,
        choices=ServiceCategory.choices,
        default=ServiceCategory.OTHER,
        help_text="Service category",
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Unit price in KES",
    )
    is_active = models.BooleanField(default=True, help_text="Whether service is available")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_services"
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Invoice(models.Model):
    """
    Invoice for hospital services.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=20, unique=True, db_index=True, help_text="Invoice number")
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="invoices",
        help_text="Patient being billed",
    )

    # Invoice details
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        help_text="Invoice status",
    )
    issue_date = models.DateField(auto_now_add=True, help_text="Date invoice was issued")
    due_date = models.DateField(help_text="Payment due date")

    # Amounts
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Subtotal before tax/discount",
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Tax amount",
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Discount amount",
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total amount due",
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Amount already paid",
    )
    balance_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Remaining balance",
    )

    # Optional references
    notes = models.TextField(blank=True, help_text="Additional notes")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_invoices",
        help_text="User who created the invoice",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_invoices"
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["patient", "status"]),
        ]

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.patient}"

    def save(self, *args, **kwargs):
        """Generate invoice number if not set."""
        if not self.invoice_number:
            self.invoice_number = self._generate_invoice_number()
        self._calculate_totals()
        super().save(*args, **kwargs)

    def _generate_invoice_number(self):
        """Generate unique invoice number."""
        from datetime import datetime

        prefix = "INV"
        date_part = datetime.now().strftime("%Y%m")
        # Get count of invoices this month
        count = Invoice.objects.filter(invoice_number__startswith=f"{prefix}{date_part}").count() + 1
        return f"{prefix}{date_part}{count:04d}"

    def _calculate_totals(self):
        """Calculate invoice totals from line items."""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.balance_due = self.total_amount - self.amount_paid

        # Update status based on payment
        if self.balance_due <= 0:
            self.status = InvoiceStatus.PAID
        elif self.amount_paid > 0:
            self.status = InvoiceStatus.PARTIALLY_PAID

    def recalculate(self):
        """Recalculate and save invoice totals."""
        self._calculate_totals()
        self.save(update_fields=["subtotal", "total_amount", "balance_due", "status", "updated_at"])


class InvoiceItem(models.Model):
    """
    Line item on an invoice.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="Parent invoice",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="invoice_items",
        help_text="Service being billed",
    )
    description = models.CharField(max_length=500, blank=True, help_text="Item description")
    quantity = models.PositiveIntegerField(default=1, help_text="Quantity")
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Price per unit",
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total price (quantity * unit_price)",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "billing_invoice_items"
        verbose_name = "Invoice Item"
        verbose_name_plural = "Invoice Items"

    def __str__(self):
        return f"{self.service.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        """Calculate total price before saving."""
        self.total_price = Decimal(str(self.quantity)) * self.unit_price
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Payment record for an invoice.

    Supports multiple payment methods including M-Pesa.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name="payments",
        help_text="Invoice being paid",
    )

    # Payment details
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.MPESA,
        help_text="Payment method",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Payment amount",
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        help_text="Payment status",
    )

    # M-Pesa specific fields
    phone_number = models.CharField(max_length=15, blank=True, help_text="M-Pesa phone number")
    merchant_request_id = models.CharField(
        max_length=100, blank=True, db_index=True, help_text="M-Pesa MerchantRequestID"
    )
    checkout_request_id = models.CharField(
        max_length=100, blank=True, db_index=True, help_text="M-Pesa CheckoutRequestID"
    )
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, db_index=True, help_text="M-Pesa Receipt Number")
    transaction_date = models.DateTimeField(null=True, blank=True, help_text="M-Pesa Transaction Date")

    # Response data
    result_code = models.CharField(max_length=10, blank=True, help_text="M-Pesa Result Code")
    result_description = models.TextField(blank=True, help_text="M-Pesa Result Description")
    callback_data = models.JSONField(null=True, blank=True, help_text="Raw callback data")

    # Metadata
    reference = models.CharField(max_length=100, blank=True, help_text="Payment reference")
    notes = models.TextField(blank=True, help_text="Payment notes")
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_payments",
        help_text="Staff who processed the payment",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_payments"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["payment_method"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Payment {self.id} - {self.amount} ({self.status})"

    def mark_completed(self, receipt_number: str = None, transaction_date=None):
        """Mark payment as completed and update invoice."""
        self.status = PaymentStatus.COMPLETED
        if receipt_number:
            self.mpesa_receipt_number = receipt_number
        if transaction_date:
            self.transaction_date = transaction_date
        self.save()

        # Update invoice
        self.invoice.amount_paid += self.amount
        self.invoice.recalculate()

    def mark_failed(self, result_code: str, result_description: str):
        """Mark payment as failed."""
        self.status = PaymentStatus.FAILED
        self.result_code = result_code
        self.result_description = result_description
        self.save()
