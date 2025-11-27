"""
Django admin configuration for billing app.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from django.contrib import admin

from .models import Invoice, InvoiceItem, Payment, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin for hospital services."""

    list_display = ["code", "name", "category", "unit_price", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["code", "name", "description"]
    ordering = ["category", "name"]


class InvoiceItemInline(admin.TabularInline):
    """Inline for invoice items."""

    model = InvoiceItem
    extra = 0
    readonly_fields = ["total_price"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin for invoices."""

    list_display = [
        "invoice_number",
        "patient",
        "status",
        "total_amount",
        "amount_paid",
        "balance_due",
        "due_date",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["invoice_number", "patient__first_name", "patient__last_name", "patient__mrn"]
    readonly_fields = [
        "invoice_number",
        "subtotal",
        "total_amount",
        "amount_paid",
        "balance_due",
        "created_at",
        "updated_at",
    ]
    inlines = [InvoiceItemInline]
    date_hierarchy = "created_at"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for payments."""

    list_display = [
        "id",
        "invoice",
        "payment_method",
        "amount",
        "status",
        "mpesa_receipt_number",
        "created_at",
    ]
    list_filter = ["status", "payment_method", "created_at"]
    search_fields = [
        "invoice__invoice_number",
        "phone_number",
        "mpesa_receipt_number",
        "checkout_request_id",
    ]
    readonly_fields = [
        "merchant_request_id",
        "checkout_request_id",
        "mpesa_receipt_number",
        "transaction_date",
        "result_code",
        "result_description",
        "callback_data",
        "created_at",
        "updated_at",
    ]
    date_hierarchy = "created_at"
