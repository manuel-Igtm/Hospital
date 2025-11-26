"""
Lab Order and Lab Result models.

Provides lab test ordering workflow with HL7 v2 validation
for results using libhl7val C module.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

import uuid
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.utils import validate_hl7_segment


class OrderStatus(models.TextChoices):
    """Lab order status workflow states."""

    PENDING = "PENDING", "Pending"  # Order created, awaiting collection
    COLLECTED = "COLLECTED", "Collected"  # Specimen collected
    IN_PROGRESS = "IN_PROGRESS", "In Progress"  # Testing in progress
    RESULTED = "RESULTED", "Resulted"  # Results available
    REVIEWED = "REVIEWED", "Reviewed"  # Results reviewed by ordering doctor
    CANCELLED = "CANCELLED", "Cancelled"  # Order cancelled


class OrderPriority(models.TextChoices):
    """Lab order priority levels."""

    ROUTINE = "ROUTINE", "Routine"
    URGENT = "URGENT", "Urgent"
    STAT = "STAT", "STAT (Immediate)"


class TestCategory(models.TextChoices):
    """Categories of lab tests."""

    HEMATOLOGY = "HEMATOLOGY", "Hematology"
    CHEMISTRY = "CHEMISTRY", "Chemistry"
    MICROBIOLOGY = "MICROBIOLOGY", "Microbiology"
    URINALYSIS = "URINALYSIS", "Urinalysis"
    IMMUNOLOGY = "IMMUNOLOGY", "Immunology"
    COAGULATION = "COAGULATION", "Coagulation"
    BLOOD_BANK = "BLOOD_BANK", "Blood Bank"
    OTHER = "OTHER", "Other"


class TestType(models.Model):
    """
    Catalog of available lab tests.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, db_index=True, help_text="Test code (e.g., CBC, BMP, UA)")
    name = models.CharField(max_length=200, help_text="Full test name")
    description = models.TextField(blank=True, help_text="Test description and purpose")
    category = models.CharField(
        max_length=20, choices=TestCategory.choices, default=TestCategory.OTHER, help_text="Test category"
    )
    loinc_code = models.CharField(max_length=20, blank=True, help_text="LOINC code for standardization")
    specimen_type = models.CharField(max_length=100, default="Blood", help_text="Required specimen type")
    turnaround_hours = models.PositiveIntegerField(default=24, help_text="Expected turnaround time in hours")
    is_active = models.BooleanField(default=True, help_text="Whether this test is currently offered")

    class Meta:
        db_table = "lab_test_types"
        verbose_name = "Test Type"
        verbose_name_plural = "Test Types"
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class LabOrder(models.Model):
    """
    Lab test order placed by a doctor for a patient.

    Tracks the full lifecycle from order creation through
    result review.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Order identification
    order_number = models.CharField(max_length=20, unique=True, db_index=True, help_text="Unique order number")

    # Relationships
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.PROTECT, related_name="lab_orders", help_text="Patient for this order"
    )
    ordering_provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ordered_labs",
        help_text="Doctor who ordered the test",
    )
    test_type = models.ForeignKey(
        TestType, on_delete=models.PROTECT, related_name="orders", help_text="Type of test ordered"
    )

    # Order details
    priority = models.CharField(
        max_length=10, choices=OrderPriority.choices, default=OrderPriority.ROUTINE, help_text="Order priority"
    )
    clinical_notes = models.TextField(blank=True, help_text="Clinical indication/reason for test")

    # Status tracking
    status = models.CharField(
        max_length=15,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True,
        help_text="Current order status",
    )

    # Specimen tracking
    specimen_collected_at = models.DateTimeField(null=True, blank=True, help_text="When specimen was collected")
    specimen_collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collected_specimens",
        help_text="Who collected the specimen",
    )

    # Timestamps
    ordered_at = models.DateTimeField(auto_now_add=True, help_text="When order was placed")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update timestamp")

    class Meta:
        db_table = "lab_orders"
        verbose_name = "Lab Order"
        verbose_name_plural = "Lab Orders"
        ordering = ["-ordered_at"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["patient", "status"]),
            models.Index(fields=["ordering_provider", "status"]),
        ]

    def __str__(self):
        return f"{self.order_number} - {self.test_type.code} for {self.patient}"

    def save(self, *args, **kwargs):
        # Generate order number if not set
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def _generate_order_number(self):
        """Generate unique order number: LAB-YYYYMMDD-XXXX"""
        import random

        date_part = datetime.now().strftime("%Y%m%d")
        random_part = str(random.randint(1000, 9999))
        return f"LAB-{date_part}-{random_part}"

    def can_transition_to(self, new_status: str) -> bool:
        """
        Check if status transition is valid.

        Valid transitions:
        PENDING -> COLLECTED, CANCELLED
        COLLECTED -> IN_PROGRESS, CANCELLED
        IN_PROGRESS -> RESULTED, CANCELLED
        RESULTED -> REVIEWED
        """
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.COLLECTED, OrderStatus.CANCELLED],
            OrderStatus.COLLECTED: [OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED],
            OrderStatus.IN_PROGRESS: [OrderStatus.RESULTED, OrderStatus.CANCELLED],
            OrderStatus.RESULTED: [OrderStatus.REVIEWED],
            OrderStatus.REVIEWED: [],
            OrderStatus.CANCELLED: [],
        }
        return new_status in valid_transitions.get(self.status, [])

    def transition_to(self, new_status: str, user=None):
        """
        Transition order to new status with validation.

        Args:
            new_status: Target status
            user: User performing the transition

        Raises:
            ValidationError: If transition is invalid
        """
        if not self.can_transition_to(new_status):
            raise ValidationError(f"Cannot transition from {self.status} to {new_status}")

        self.status = new_status

        # Handle status-specific logic
        if new_status == OrderStatus.COLLECTED and user:
            self.specimen_collected_at = datetime.now()
            self.specimen_collected_by = user

        self.save()


class LabResult(models.Model):
    """
    Lab test result with HL7 v2 data storage.

    Results are validated using the libhl7val C module
    before storage.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to order
    order = models.OneToOneField(
        LabOrder, on_delete=models.CASCADE, related_name="result", help_text="Associated lab order"
    )

    # Result data (HL7 format)
    hl7_obr_segment = models.TextField(blank=True, help_text="HL7 OBR (Observation Request) segment")
    hl7_obx_segments = models.TextField(blank=True, help_text="HL7 OBX (Observation Result) segments, one per line")

    # Parsed result summary
    result_summary = models.TextField(blank=True, help_text="Human-readable result summary")

    # Flags
    is_abnormal = models.BooleanField(default=False, help_text="Whether any results are outside normal range")
    is_critical = models.BooleanField(default=False, help_text="Whether results require immediate attention")

    # Result entry
    resulted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="entered_results",
        help_text="Lab tech who entered results",
    )
    resulted_at = models.DateTimeField(auto_now_add=True, help_text="When results were entered")

    # Review tracking
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_results",
        help_text="Doctor who reviewed results",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, help_text="When results were reviewed")
    review_notes = models.TextField(blank=True, help_text="Notes from reviewing physician")

    class Meta:
        db_table = "lab_results"
        verbose_name = "Lab Result"
        verbose_name_plural = "Lab Results"
        ordering = ["-resulted_at"]

    def __str__(self):
        return f"Result for {self.order.order_number}"

    def clean(self):
        """Validate HL7 segments before saving."""
        super().clean()

        # Validate OBR segment if provided
        if self.hl7_obr_segment:
            try:
                validate_hl7_segment(self.hl7_obr_segment)
                if not self.hl7_obr_segment.startswith("OBR|"):
                    raise ValidationError({"hl7_obr_segment": "Segment must be an OBR segment"})
            except ValueError as e:
                raise ValidationError({"hl7_obr_segment": f"Invalid HL7 OBR segment: {e}"})

        # Validate OBX segments if provided
        if self.hl7_obx_segments:
            for i, segment in enumerate(self.hl7_obx_segments.strip().split("\n")):
                segment = segment.strip()
                if not segment:
                    continue
                try:
                    validate_hl7_segment(segment)
                    if not segment.startswith("OBX|"):
                        raise ValidationError({"hl7_obx_segments": f"Line {i+1}: Segment must be an OBX segment"})
                except ValueError as e:
                    raise ValidationError({"hl7_obx_segments": f"Line {i+1}: Invalid HL7 OBX segment: {e}"})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_obx_list(self) -> list[str]:
        """Return OBX segments as a list."""
        if not self.hl7_obx_segments:
            return []
        return [s.strip() for s in self.hl7_obx_segments.split("\n") if s.strip()]

    def parse_obx_values(self) -> list[dict]:
        """
        Parse OBX segments into structured data.

        Returns list of dicts with keys:
        - set_id: OBX sequence number
        - value_type: Type of value (NM, ST, etc.)
        - identifier: Test identifier code
        - value: Actual result value
        - units: Units of measurement
        - reference_range: Normal range
        - abnormal_flag: H (high), L (low), A (abnormal), etc.
        """
        results = []
        for segment in self.get_obx_list():
            fields = segment.split("|")
            if len(fields) >= 6:
                result = {
                    "set_id": fields[1] if len(fields) > 1 else "",
                    "value_type": fields[2] if len(fields) > 2 else "",
                    "identifier": fields[3] if len(fields) > 3 else "",
                    "value": fields[5] if len(fields) > 5 else "",
                    "units": fields[6] if len(fields) > 6 else "",
                    "reference_range": fields[7] if len(fields) > 7 else "",
                    "abnormal_flag": fields[8] if len(fields) > 8 else "",
                }
                results.append(result)
        return results
