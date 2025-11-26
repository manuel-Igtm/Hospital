"""
Lab Order serializers for API endpoints.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from django.utils import timezone

from rest_framework import serializers

from apps.patients.serializers import PatientListSerializer
from apps.users.serializers import UserSerializer

from .models import (
    LabOrder,
    LabResult,
    OrderPriority,
    OrderStatus,
    TestCategory,
    TestType,
)


class TestTypeSerializer(serializers.ModelSerializer):
    """Serializer for test type catalog."""

    class Meta:
        model = TestType
        fields = [
            "id",
            "code",
            "name",
            "description",
            "category",
            "loinc_code",
            "specimen_type",
            "turnaround_hours",
            "is_active",
        ]
        read_only_fields = ["id"]


class LabOrderListSerializer(serializers.ModelSerializer):
    """Serializer for lab order list view."""

    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    patient_mrn = serializers.CharField(source="patient.mrn", read_only=True)
    test_code = serializers.CharField(source="test_type.code", read_only=True)
    test_name = serializers.CharField(source="test_type.name", read_only=True)
    ordering_provider_name = serializers.CharField(source="ordering_provider.full_name", read_only=True)
    has_result = serializers.SerializerMethodField()

    class Meta:
        model = LabOrder
        fields = [
            "id",
            "order_number",
            "patient",
            "patient_name",
            "patient_mrn",
            "test_type",
            "test_code",
            "test_name",
            "ordering_provider",
            "ordering_provider_name",
            "priority",
            "status",
            "has_result",
            "ordered_at",
        ]

    def get_has_result(self, obj):
        return hasattr(obj, "result")


class LabOrderDetailSerializer(serializers.ModelSerializer):
    """Serializer for lab order detail view."""

    patient = PatientListSerializer(read_only=True)
    test_type = TestTypeSerializer(read_only=True)
    ordering_provider = UserSerializer(read_only=True)
    specimen_collected_by = UserSerializer(read_only=True)
    result = serializers.SerializerMethodField()
    allowed_transitions = serializers.SerializerMethodField()

    class Meta:
        model = LabOrder
        fields = [
            "id",
            "order_number",
            "patient",
            "test_type",
            "ordering_provider",
            "priority",
            "clinical_notes",
            "status",
            "specimen_collected_at",
            "specimen_collected_by",
            "ordered_at",
            "updated_at",
            "result",
            "allowed_transitions",
        ]

    def get_result(self, obj):
        if hasattr(obj, "result"):
            return LabResultSerializer(obj.result).data
        return None

    def get_allowed_transitions(self, obj):
        """Return list of valid status transitions."""
        transitions = []
        for status in OrderStatus.values:
            if obj.can_transition_to(status):
                transitions.append(status)
        return transitions


class LabOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new lab orders."""

    class Meta:
        model = LabOrder
        fields = ["patient", "test_type", "priority", "clinical_notes"]

    def validate_patient(self, value):
        """Ensure patient is active."""
        if not value.is_active:
            raise serializers.ValidationError("Cannot order tests for inactive patients.")
        return value

    def validate_test_type(self, value):
        """Ensure test type is active."""
        if not value.is_active:
            raise serializers.ValidationError("This test is not currently available.")
        return value

    def create(self, validated_data):
        """Create order with ordering provider from request."""
        validated_data["ordering_provider"] = self.context["request"].user
        return super().create(validated_data)


class LabOrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for status transitions."""

    status = serializers.ChoiceField(choices=OrderStatus.choices)

    def validate_status(self, value):
        """Validate the status transition."""
        order = self.context.get("order")
        if order and not order.can_transition_to(value):
            raise serializers.ValidationError(f"Cannot transition from {order.status} to {value}")
        return value


class LabResultSerializer(serializers.ModelSerializer):
    """Serializer for lab results."""

    resulted_by = UserSerializer(read_only=True)
    reviewed_by = UserSerializer(read_only=True)
    parsed_results = serializers.SerializerMethodField()

    class Meta:
        model = LabResult
        fields = [
            "id",
            "order",
            "hl7_obr_segment",
            "hl7_obx_segments",
            "result_summary",
            "is_abnormal",
            "is_critical",
            "resulted_by",
            "resulted_at",
            "reviewed_by",
            "reviewed_at",
            "review_notes",
            "parsed_results",
        ]
        read_only_fields = ["id", "resulted_by", "resulted_at", "reviewed_by", "reviewed_at"]

    def get_parsed_results(self, obj):
        """Return parsed OBX values."""
        return obj.parse_obx_values()


class LabResultCreateSerializer(serializers.ModelSerializer):
    """Serializer for entering lab results."""

    class Meta:
        model = LabResult
        fields = ["order", "hl7_obr_segment", "hl7_obx_segments", "result_summary", "is_abnormal", "is_critical"]

    def validate_order(self, value):
        """Ensure order is in correct status for results."""
        if value.status not in [OrderStatus.COLLECTED, OrderStatus.IN_PROGRESS]:
            raise serializers.ValidationError("Can only enter results for collected or in-progress orders.")
        if hasattr(value, "result"):
            raise serializers.ValidationError("Results already exist for this order.")
        return value

    def validate(self, attrs):
        """Validate HL7 segments."""
        # The model's clean() method will validate HL7 format
        return attrs

    def create(self, validated_data):
        """Create result and update order status."""
        validated_data["resulted_by"] = self.context["request"].user
        result = super().create(validated_data)

        # Update order status to RESULTED
        order = result.order
        order.status = OrderStatus.RESULTED
        order.save()

        return result


class LabResultReviewSerializer(serializers.Serializer):
    """Serializer for reviewing lab results."""

    review_notes = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        """Mark result as reviewed."""
        instance.reviewed_by = self.context["request"].user
        instance.reviewed_at = timezone.now()
        instance.review_notes = validated_data.get("review_notes", "")
        instance.save()

        # Update order status to REVIEWED
        instance.order.status = OrderStatus.REVIEWED
        instance.order.save()

        return instance
