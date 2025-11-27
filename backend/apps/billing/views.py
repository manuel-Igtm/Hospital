"""
Billing views for invoices and M-Pesa payments.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

import logging

from django.db.models import Q
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import UserRole

from .models import Invoice, InvoiceStatus, Payment, PaymentMethod, PaymentStatus, Service
from .mpesa import MpesaError, MpesaService
from .serializers import (
    InvoiceCreateSerializer,
    InvoiceSerializer,
    MpesaCallbackSerializer,
    MpesaPaymentInitiateSerializer,
    PaymentSerializer,
    ServiceSerializer,
)

logger = logging.getLogger(__name__)


class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for hospital services."""

    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["category", "is_active"]
    search_fields = ["code", "name", "description"]
    ordering_fields = ["name", "unit_price", "category", "created_at"]
    ordering = ["created_at"]

    def get_queryset(self):
        """Filter services based on user role."""
        queryset = super().get_queryset()

        # Non-admin users can only see active services
        if not self.request.user.role == UserRole.ADMIN:
            queryset = queryset.filter(is_active=True)

        return queryset

    def perform_destroy(self, instance):
        """Soft delete services."""
        instance.is_active = False
        instance.save()


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for invoices."""

    queryset = Invoice.objects.select_related("patient", "created_by").prefetch_related("items")
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "patient"]
    search_fields = ["invoice_number", "patient__first_name", "patient__last_name", "patient__mrn"]
    ordering_fields = ["created_at", "due_date", "total_amount"]
    ordering = ["created_at"]

    def get_serializer_class(self):
        """Use different serializer for create."""
        if self.action == "create":
            return InvoiceCreateSerializer
        return InvoiceSerializer

    def create(self, request, *args, **kwargs):
        """Create invoice and return with full serialization."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()
        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        """Filter invoices based on user role and query params."""
        queryset = super().get_queryset()

        # Filter by status
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by patient
        patient_id = self.request.query_params.get("patient_id")
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        # Filter overdue invoices
        if self.request.query_params.get("overdue") == "true":
            queryset = queryset.filter(
                due_date__lt=timezone.now().date(),
                status__in=[InvoiceStatus.PENDING, InvoiceStatus.PARTIALLY_PAID],
            )

        return queryset

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel an invoice."""
        invoice = self.get_object()

        if invoice.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED]:
            return Response(
                {"error": "Cannot cancel this invoice"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invoice.status = InvoiceStatus.CANCELLED
        invoice.save()

        return Response(InvoiceSerializer(invoice).data)

    @action(detail=True, methods=["get"])
    def payments(self, request, pk=None):
        """Get payments for an invoice."""
        invoice = self.get_object()
        payments = Payment.objects.filter(invoice=invoice).order_by("-created_at")
        return Response(PaymentSerializer(payments, many=True).data)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for payments (read-only, payments created via M-Pesa endpoints)."""

    queryset = Payment.objects.select_related("invoice", "invoice__patient")
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "payment_method", "invoice"]
    search_fields = ["invoice__invoice_number", "mpesa_receipt_number", "phone_number"]
    ordering_fields = ["created_at", "amount"]
    ordering = ["created_at"]


class MpesaSTKPushView(APIView):
    """
    Initiate M-Pesa STK Push payment.

    POST /api/v1/billing/mpesa/stk-push/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Initiate STK Push to customer's phone."""
        serializer = MpesaPaymentInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invoice = Invoice.objects.get(id=serializer.validated_data["invoice_id"])
        phone_number = serializer.validated_data["phone_number"]
        amount = int(serializer.validated_data["amount"])

        # Create pending payment record
        payment = Payment.objects.create(
            invoice=invoice,
            payment_method=PaymentMethod.MPESA,
            amount=amount,
            phone_number=phone_number,
            status=PaymentStatus.PENDING,
            processed_by=request.user,
        )

        try:
            # Initiate STK Push
            mpesa = MpesaService()
            result = mpesa.initiate_stk_push(
                phone_number=phone_number,
                amount=amount,
                account_reference=invoice.invoice_number,
                transaction_desc="Hospital Bill",
            )

            if result["success"]:
                # Update payment with M-Pesa request IDs
                payment.merchant_request_id = result["merchant_request_id"]
                payment.checkout_request_id = result["checkout_request_id"]
                payment.status = PaymentStatus.PROCESSING
                payment.save()

                return Response(
                    {
                        "success": True,
                        "message": "STK Push sent to your phone",
                        "payment_id": str(payment.id),
                        "checkout_request_id": result["checkout_request_id"],
                        "customer_message": result["customer_message"],
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                payment.status = PaymentStatus.FAILED
                payment.result_description = result.get("response_description", "STK Push failed")
                payment.save()

                return Response(
                    {
                        "success": False,
                        "error": result.get("response_description", "Failed to initiate payment"),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except MpesaError as e:
            payment.status = PaymentStatus.FAILED
            payment.result_description = str(e)
            payment.save()

            logger.error(f"M-Pesa STK Push error: {e}")
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MpesaCallbackView(APIView):
    """
    Handle M-Pesa callback after STK Push.

    POST /api/v1/billing/mpesa/callback/
    """

    permission_classes = [AllowAny]  # M-Pesa calls this endpoint

    def post(self, request):
        """Process M-Pesa callback."""
        logger.info(f"M-Pesa callback received: {request.data}")

        serializer = MpesaCallbackSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Invalid callback data: {serializer.errors}")
            return Response({"ResultCode": 1, "ResultDesc": "Invalid data"})

        # Parse callback data
        parsed = MpesaService.parse_callback(request.data)

        # Find the payment
        checkout_request_id = parsed.get("checkout_request_id")
        if not checkout_request_id:
            logger.error("Missing CheckoutRequestID in callback")
            return Response({"ResultCode": 1, "ResultDesc": "Missing CheckoutRequestID"})

        try:
            payment = Payment.objects.get(checkout_request_id=checkout_request_id)
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for CheckoutRequestID: {checkout_request_id}")
            return Response({"ResultCode": 0, "ResultDesc": "Accepted"})

        # Store raw callback data
        payment.callback_data = request.data
        payment.result_code = parsed["result_code"]
        payment.result_description = parsed["result_desc"]

        if parsed["success"]:
            # Payment successful
            payment.mark_completed(
                receipt_number=parsed.get("receipt_number"),
                transaction_date=parsed.get("transaction_date"),
            )
            logger.info(f"Payment {payment.id} completed successfully")
        else:
            # Payment failed
            payment.mark_failed(parsed["result_code"], parsed["result_desc"])
            logger.warning(f"Payment {payment.id} failed: {parsed['result_desc']}")

        # Always respond with success to M-Pesa
        return Response({"ResultCode": 0, "ResultDesc": "Accepted"})


class MpesaQueryView(APIView):
    """
    Query M-Pesa transaction status.

    GET /api/v1/billing/mpesa/query/<payment_id>/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        """Query payment status from M-Pesa."""
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not payment.checkout_request_id:
            return Response(
                {"error": "No M-Pesa transaction to query"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If already completed or failed, return cached status
        if payment.status in [PaymentStatus.COMPLETED, PaymentStatus.FAILED]:
            return Response(PaymentSerializer(payment).data)

        try:
            mpesa = MpesaService()
            result = mpesa.query_stk_status(payment.checkout_request_id)

            if result["success"]:
                # Transaction was successful (might have been processed via callback already)
                if payment.status != PaymentStatus.COMPLETED:
                    payment.mark_completed()
            elif result["result_code"] in ["1032", "1037"]:
                # Cancelled or timeout
                payment.status = PaymentStatus.CANCELLED if result["result_code"] == "1032" else PaymentStatus.TIMEOUT
                payment.result_code = result["result_code"]
                payment.result_description = result["result_desc"]
                payment.save()

            return Response(PaymentSerializer(payment).data)

        except MpesaError as e:
            logger.error(f"M-Pesa query error: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
