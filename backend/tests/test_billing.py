"""
Tests for billing app - services, invoices, and payments.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.urls import reverse

from rest_framework import status

import pytest

from apps.billing.models import (
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
    Service,
    ServiceCategory,
)
from apps.billing.mpesa import MpesaService
from apps.patients.models import Patient


@pytest.fixture
def test_patient(db):
    """Create a test patient."""
    return Patient.objects.create(
        first_name="Test",
        last_name="Patient",
        date_of_birth=date(1990, 1, 1),
        email="patient@test.com",
        phone="+254700000000",
    )


@pytest.fixture
def test_service(db):
    """Create a test service."""
    return Service.objects.create(
        code="LAB001",
        name="Complete Blood Count",
        description="Full blood count test",
        category=ServiceCategory.LABORATORY,
        unit_price=Decimal("500.00"),
    )


@pytest.fixture
def test_invoice(db, test_patient, test_service, admin_user):
    """Create a test invoice with items."""
    invoice = Invoice.objects.create(
        patient=test_patient,
        due_date=date.today() + timedelta(days=30),
        status=InvoiceStatus.PENDING,
        created_by=admin_user,
    )
    InvoiceItem.objects.create(
        invoice=invoice,
        service=test_service,
        quantity=1,
        unit_price=test_service.unit_price,
    )
    invoice.recalculate()
    return invoice


class TestServiceEndpoints:
    """Tests for service CRUD operations."""

    def test_list_services(self, authenticated_admin_client, test_service):
        """Test listing services."""
        url = reverse("service-list")
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_create_service(self, authenticated_admin_client):
        """Test creating a service."""
        url = reverse("service-list")
        data = {
            "code": "CONS001",
            "name": "General Consultation",
            "description": "General doctor consultation",
            "category": ServiceCategory.CONSULTATION,
            "unit_price": "1000.00",
        }
        response = authenticated_admin_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "General Consultation"
        assert Decimal(response.data["unit_price"]) == Decimal("1000.00")

    def test_filter_services_by_category(self, authenticated_admin_client, test_service):
        """Test filtering services by category."""
        url = reverse("service-list")
        response = authenticated_admin_client.get(url, {"category": ServiceCategory.LABORATORY})

        assert response.status_code == status.HTTP_200_OK
        for service in response.data["results"]:
            assert service["category"] == ServiceCategory.LABORATORY


class TestInvoiceEndpoints:
    """Tests for invoice operations."""

    def test_list_invoices(self, authenticated_admin_client, test_invoice):
        """Test listing invoices."""
        url = reverse("invoice-list")
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_create_invoice(self, authenticated_admin_client, test_patient, test_service):
        """Test creating an invoice with items."""
        url = reverse("invoice-list")
        data = {
            "patient_id": str(test_patient.id),
            "due_date": str(date.today() + timedelta(days=30)),
            "items": [
                {
                    "service_id": str(test_service.id),
                    "quantity": 2,
                }
            ],
        }
        response = authenticated_admin_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        # The response returns the patient ID under 'patient'
        assert "invoice_number" in response.data
        assert Decimal(response.data["total_amount"]) == Decimal("1000.00")

    def test_get_invoice_detail(self, authenticated_admin_client, test_invoice):
        """Test getting invoice details."""
        url = reverse("invoice-detail", kwargs={"pk": test_invoice.id})
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["invoice_number"] == test_invoice.invoice_number
        assert len(response.data["items"]) == 1

    def test_cancel_invoice(self, authenticated_admin_client, test_invoice):
        """Test cancelling an invoice."""
        # Ensure invoice is in PENDING status
        test_invoice.status = InvoiceStatus.PENDING
        test_invoice.save()
        test_invoice.refresh_from_db()

        url = reverse("invoice-cancel", kwargs={"pk": test_invoice.id})
        response = authenticated_admin_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == InvoiceStatus.CANCELLED

    def test_cannot_cancel_paid_invoice(self, authenticated_admin_client, test_patient, test_service, admin_user):
        """Test that paid invoices cannot be cancelled."""
        # Create a separate paid invoice for this test
        paid_invoice = Invoice.objects.create(
            patient=test_patient,
            due_date=date.today() + timedelta(days=30),
            status=InvoiceStatus.PAID,
            created_by=admin_user,
        )

        url = reverse("invoice-cancel", kwargs={"pk": paid_invoice.id})
        response = authenticated_admin_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_invoice_payments(self, authenticated_admin_client, test_invoice):
        """Test getting payments for an invoice."""
        # Create a payment
        Payment.objects.create(
            invoice=test_invoice,
            payment_method=PaymentMethod.CASH,
            amount=Decimal("100.00"),
            status=PaymentStatus.COMPLETED,
        )

        url = reverse("invoice-payments", kwargs={"pk": test_invoice.id})
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1


class TestPaymentEndpoints:
    """Tests for payment operations."""

    def test_list_payments(self, authenticated_admin_client, test_invoice):
        """Test listing payments."""
        Payment.objects.create(
            invoice=test_invoice,
            payment_method=PaymentMethod.MPESA,
            amount=Decimal("500.00"),
            status=PaymentStatus.COMPLETED,
        )

        url = reverse("payment-list")
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1


class TestMpesaIntegration:
    """Tests for M-Pesa integration."""

    @patch("apps.billing.views.MpesaService")
    def test_stk_push_initiation(self, mock_mpesa_class, authenticated_admin_client, test_invoice):
        """Test initiating STK Push payment."""
        # Ensure invoice is in payable state
        test_invoice.status = InvoiceStatus.PENDING
        test_invoice.save()
        test_invoice.refresh_from_db()

        mock_mpesa = MagicMock()
        mock_mpesa.initiate_stk_push.return_value = {
            "success": True,
            "merchant_request_id": "12345",
            "checkout_request_id": "67890",
            "response_code": "0",
            "response_description": "Success",
            "customer_message": "Enter PIN",
        }
        mock_mpesa_class.return_value = mock_mpesa

        url = reverse("mpesa-stk-push")
        data = {
            "invoice_id": str(test_invoice.id),
            "phone_number": "0700000000",
            "amount": "500.00",
        }
        response = authenticated_admin_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "payment_id" in response.data

    def test_stk_push_validation(self, authenticated_admin_client, test_invoice):
        """Test STK Push validation errors."""
        url = reverse("mpesa-stk-push")

        # Test missing phone number
        data = {
            "invoice_id": str(test_invoice.id),
        }
        response = authenticated_admin_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_mpesa_callback_success(self, api_client, test_invoice):
        """Test successful M-Pesa callback."""
        # Create a pending payment
        payment = Payment.objects.create(
            invoice=test_invoice,
            payment_method=PaymentMethod.MPESA,
            amount=Decimal("500.00"),
            phone_number="254700000000",
            merchant_request_id="12345",
            checkout_request_id="67890",
            status=PaymentStatus.PROCESSING,
        )

        url = reverse("mpesa-callback")
        callback_data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "12345",
                    "CheckoutRequestID": "67890",
                    "ResultCode": 0,
                    "ResultDesc": "Success",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 500},
                            {"Name": "MpesaReceiptNumber", "Value": "ABC123XYZ"},
                            {"Name": "TransactionDate", "Value": 20240115123456},
                            {"Name": "PhoneNumber", "Value": 254700000000},
                        ]
                    },
                }
            }
        }
        response = api_client.post(url, callback_data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Verify payment was updated
        payment.refresh_from_db()
        assert payment.status == PaymentStatus.COMPLETED
        assert payment.mpesa_receipt_number == "ABC123XYZ"

    def test_mpesa_callback_failure(self, api_client, test_invoice):
        """Test failed M-Pesa callback."""
        payment = Payment.objects.create(
            invoice=test_invoice,
            payment_method=PaymentMethod.MPESA,
            amount=Decimal("500.00"),
            phone_number="254700000000",
            checkout_request_id="67890",
            status=PaymentStatus.PROCESSING,
        )

        url = reverse("mpesa-callback")
        callback_data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "12345",
                    "CheckoutRequestID": "67890",
                    "ResultCode": 1032,
                    "ResultDesc": "Request cancelled by user",
                }
            }
        }
        response = api_client.post(url, callback_data, format="json")

        assert response.status_code == status.HTTP_200_OK

        payment.refresh_from_db()
        assert payment.status == PaymentStatus.FAILED


class TestInvoiceModel:
    """Tests for Invoice model methods."""

    def test_invoice_number_generation(self, db, test_patient, admin_user):
        """Test that invoice numbers are generated correctly."""
        invoice = Invoice.objects.create(
            patient=test_patient,
            due_date=date.today() + timedelta(days=30),
            created_by=admin_user,
        )

        assert invoice.invoice_number.startswith("INV")
        assert len(invoice.invoice_number) == 13  # INV + YYYYMM + 0001

    def test_invoice_recalculation(self, db, test_invoice, test_service):
        """Test invoice total recalculation."""
        # Add another item
        InvoiceItem.objects.create(
            invoice=test_invoice,
            service=test_service,
            quantity=2,
            unit_price=Decimal("500.00"),
        )
        test_invoice.recalculate()

        assert test_invoice.subtotal == Decimal("1500.00")
        assert test_invoice.total_amount == Decimal("1500.00")


class TestMpesaService:
    """Tests for MpesaService class."""

    def test_phone_number_formatting(self):
        """Test phone number formatting."""
        service = MpesaService()

        assert service._format_phone_number("0700000000") == "254700000000"
        assert service._format_phone_number("+254700000000") == "254700000000"
        assert service._format_phone_number("254700000000") == "254700000000"
        assert service._format_phone_number("700000000") == "254700000000"

    def test_callback_parsing_success(self):
        """Test parsing successful callback data."""
        callback_data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "12345",
                    "CheckoutRequestID": "67890",
                    "ResultCode": 0,
                    "ResultDesc": "Success",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 500},
                            {"Name": "MpesaReceiptNumber", "Value": "ABC123"},
                            {"Name": "TransactionDate", "Value": 20240115123456},
                            {"Name": "PhoneNumber", "Value": 254700000000},
                        ]
                    },
                }
            }
        }

        result = MpesaService.parse_callback(callback_data)

        assert result["success"] is True
        assert result["amount"] == 500
        assert result["receipt_number"] == "ABC123"

    def test_callback_parsing_failure(self):
        """Test parsing failed callback data."""
        callback_data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "12345",
                    "CheckoutRequestID": "67890",
                    "ResultCode": 1032,
                    "ResultDesc": "Request cancelled by user",
                }
            }
        }

        result = MpesaService.parse_callback(callback_data)

        assert result["success"] is False
        assert result["result_code"] == "1032"
