"""
Billing serializers for invoices and payments.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from decimal import Decimal

from rest_framework import serializers

from apps.patients.models import Patient

from .models import Invoice, InvoiceItem, InvoiceStatus, Payment, PaymentMethod, PaymentStatus, Service


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for hospital services."""

    class Meta:
        model = Service
        fields = [
            "id",
            "code",
            "name",
            "description",
            "category",
            "unit_price",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for invoice line items."""

    service_name = serializers.CharField(source="service.name", read_only=True)
    service_code = serializers.CharField(source="service.code", read_only=True)

    class Meta:
        model = InvoiceItem
        fields = [
            "id",
            "service",
            "service_name",
            "service_code",
            "description",
            "quantity",
            "unit_price",
            "total_price",
        ]
        read_only_fields = ["id", "total_price"]


class InvoiceItemCreateSerializer(serializers.Serializer):
    """Serializer for creating invoice items."""

    service_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_service_id(self, value):
        """Validate service exists."""
        try:
            Service.objects.get(id=value, is_active=True)
        except Service.DoesNotExist:
            raise serializers.ValidationError("Service not found or inactive")
        return value


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoices."""

    items = InvoiceItemSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    patient_mrn = serializers.CharField(source="patient.mrn", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "patient",
            "patient_name",
            "patient_mrn",
            "status",
            "status_display",
            "issue_date",
            "due_date",
            "subtotal",
            "tax_amount",
            "discount_amount",
            "total_amount",
            "amount_paid",
            "balance_due",
            "notes",
            "items",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "invoice_number",
            "subtotal",
            "total_amount",
            "amount_paid",
            "balance_due",
            "created_by",
            "created_at",
            "updated_at",
        ]


class InvoiceCreateSerializer(serializers.Serializer):
    """Serializer for creating invoices with items."""

    patient_id = serializers.UUIDField()
    due_date = serializers.DateField()
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    notes = serializers.CharField(required=False, allow_blank=True)
    items = InvoiceItemCreateSerializer(many=True, min_length=1)

    def validate_patient_id(self, value):
        """Validate patient exists."""
        try:
            Patient.objects.get(id=value, is_active=True)
        except Patient.DoesNotExist:
            raise serializers.ValidationError("Patient not found or inactive")
        return value

    def create(self, validated_data):
        """Create invoice with items."""
        items_data = validated_data.pop("items")
        patient = Patient.objects.get(id=validated_data.pop("patient_id"))

        invoice = Invoice.objects.create(
            patient=patient,
            due_date=validated_data["due_date"],
            tax_amount=validated_data.get("tax_amount", Decimal("0.00")),
            discount_amount=validated_data.get("discount_amount", Decimal("0.00")),
            notes=validated_data.get("notes", ""),
            status=InvoiceStatus.PENDING,
            created_by=self.context["request"].user,
        )

        # Create invoice items
        for item_data in items_data:
            service = Service.objects.get(id=item_data["service_id"])
            InvoiceItem.objects.create(
                invoice=invoice,
                service=service,
                quantity=item_data.get("quantity", 1),
                unit_price=item_data.get("unit_price", service.unit_price),
                description=item_data.get("description", ""),
            )

        # Recalculate totals
        invoice.recalculate()

        return invoice


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments."""

    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_method_display = serializers.CharField(source="get_payment_method_display", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "invoice",
            "invoice_number",
            "payment_method",
            "payment_method_display",
            "amount",
            "status",
            "status_display",
            "phone_number",
            "merchant_request_id",
            "checkout_request_id",
            "mpesa_receipt_number",
            "transaction_date",
            "result_code",
            "result_description",
            "reference",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "merchant_request_id",
            "checkout_request_id",
            "mpesa_receipt_number",
            "transaction_date",
            "result_code",
            "result_description",
            "created_at",
            "updated_at",
        ]


class MpesaPaymentInitiateSerializer(serializers.Serializer):
    """Serializer for initiating M-Pesa STK Push payment."""

    invoice_id = serializers.UUIDField()
    phone_number = serializers.CharField(max_length=15)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)

    def validate_invoice_id(self, value):
        """Validate invoice exists and is payable."""
        try:
            invoice = Invoice.objects.get(id=value)
            if invoice.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED]:
                raise serializers.ValidationError("Invoice is not payable")
            return value
        except Invoice.DoesNotExist:
            raise serializers.ValidationError("Invoice not found")

    def validate_phone_number(self, value):
        """Validate phone number format."""
        # Remove spaces and special characters
        phone = "".join(filter(str.isdigit, value))
        if len(phone) < 9 or len(phone) > 15:
            raise serializers.ValidationError("Invalid phone number")
        return value

    def validate(self, data):
        """Validate amount against invoice balance."""
        invoice = Invoice.objects.get(id=data["invoice_id"])

        if "amount" not in data or data["amount"] is None:
            data["amount"] = invoice.balance_due
        elif data["amount"] > invoice.balance_due:
            raise serializers.ValidationError({"amount": "Amount exceeds invoice balance"})
        elif data["amount"] <= 0:
            raise serializers.ValidationError({"amount": "Amount must be positive"})

        return data


class MpesaCallbackSerializer(serializers.Serializer):
    """Serializer for M-Pesa callback data."""

    Body = serializers.DictField()


class PaymentQuerySerializer(serializers.Serializer):
    """Serializer for querying payment status."""

    payment_id = serializers.UUIDField()
