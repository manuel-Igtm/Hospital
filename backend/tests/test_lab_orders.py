"""
Tests for the lab_orders app.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from datetime import date

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status

import pytest

from apps.lab_orders.models import (
    LabOrder,
    LabResult,
    OrderPriority,
    OrderStatus,
    TestCategory,
    TestType,
)
from apps.patients.models import Patient


@pytest.fixture
def test_type(db):
    """Create a sample test type."""
    return TestType.objects.create(
        code="CBC",
        name="Complete Blood Count",
        description="Measures various blood components",
        category=TestCategory.HEMATOLOGY,
        loinc_code="58410-2",
        specimen_type="Blood",
        turnaround_hours=4,
    )


@pytest.fixture
def test_type_chemistry(db):
    """Create a chemistry test type."""
    return TestType.objects.create(
        code="BMP",
        name="Basic Metabolic Panel",
        description="Measures electrolytes and kidney function",
        category=TestCategory.CHEMISTRY,
        specimen_type="Blood",
        turnaround_hours=2,
    )


@pytest.fixture
def sample_patient(db):
    """Create a sample patient for lab orders."""
    return Patient.objects.create(
        first_name="Lab",
        last_name="Patient",
        date_of_birth=date(1985, 6, 15),
    )


@pytest.fixture
def lab_order(db, sample_patient, test_type, doctor_user):
    """Create a sample lab order."""
    return LabOrder.objects.create(
        patient=sample_patient,
        ordering_provider=doctor_user,
        test_type=test_type,
        priority=OrderPriority.ROUTINE,
        clinical_notes="Annual checkup",
    )


@pytest.mark.django_db
class TestTestTypeModel:
    """Tests for TestType model."""

    def test_create_test_type(self, test_type):
        """Test creating a test type."""
        assert test_type.pk is not None
        assert test_type.code == "CBC"
        assert test_type.category == TestCategory.HEMATOLOGY
        assert test_type.is_active

    def test_test_type_str(self, test_type):
        """Test string representation."""
        assert str(test_type) == "CBC - Complete Blood Count"


@pytest.mark.django_db
class TestLabOrderModel:
    """Tests for LabOrder model."""

    def test_create_lab_order(self, lab_order):
        """Test creating a lab order."""
        assert lab_order.pk is not None
        assert lab_order.order_number.startswith("LAB-")
        assert lab_order.status == OrderStatus.PENDING

    def test_order_number_auto_generated(self, sample_patient, test_type, doctor_user):
        """Test order number is auto-generated."""
        order = LabOrder.objects.create(
            patient=sample_patient,
            ordering_provider=doctor_user,
            test_type=test_type,
        )
        assert order.order_number is not None
        assert order.order_number.startswith("LAB-")

    def test_status_transitions(self, lab_order):
        """Test valid status transitions."""
        # PENDING -> COLLECTED
        assert lab_order.can_transition_to(OrderStatus.COLLECTED)
        lab_order.transition_to(OrderStatus.COLLECTED)
        assert lab_order.status == OrderStatus.COLLECTED

        # COLLECTED -> IN_PROGRESS
        assert lab_order.can_transition_to(OrderStatus.IN_PROGRESS)
        lab_order.transition_to(OrderStatus.IN_PROGRESS)
        assert lab_order.status == OrderStatus.IN_PROGRESS

    def test_invalid_status_transition(self, lab_order):
        """Test invalid status transitions raise error."""
        # PENDING cannot go directly to RESULTED
        assert not lab_order.can_transition_to(OrderStatus.RESULTED)

        with pytest.raises(DjangoValidationError):
            lab_order.transition_to(OrderStatus.RESULTED)

    def test_cancel_order(self, lab_order):
        """Test cancelling an order."""
        assert lab_order.can_transition_to(OrderStatus.CANCELLED)
        lab_order.transition_to(OrderStatus.CANCELLED)
        assert lab_order.status == OrderStatus.CANCELLED

        # Cannot transition from cancelled
        assert not lab_order.can_transition_to(OrderStatus.COLLECTED)

    def test_specimen_collection_tracking(self, lab_order, nurse_user):
        """Test specimen collection updates fields."""
        lab_order.transition_to(OrderStatus.COLLECTED, user=nurse_user)

        assert lab_order.specimen_collected_at is not None
        assert lab_order.specimen_collected_by == nurse_user


@pytest.mark.django_db
class TestLabResultModel:
    """Tests for LabResult model."""

    def test_create_result(self, lab_order, lab_tech_user):
        """Test creating a lab result."""
        # First transition order to collected
        lab_order.transition_to(OrderStatus.COLLECTED)

        result = LabResult.objects.create(
            order=lab_order,
            hl7_obr_segment="OBR|1|12345|67890|58410-2^CBC^LN|||20231115120000",
            hl7_obx_segments="OBX|1|NM|WBC^White Blood Cell Count||7.5|10*3/uL|4.5-11.0|N",
            result_summary="WBC: 7.5 (Normal)",
            resulted_by=lab_tech_user,
        )

        assert result.pk is not None
        assert result.order == lab_order

    def test_hl7_obr_validation(self, lab_order, lab_tech_user):
        """Test OBR segment validation."""
        lab_order.transition_to(OrderStatus.COLLECTED)

        # Invalid OBR (doesn't start with OBR|)
        with pytest.raises(DjangoValidationError) as exc_info:
            LabResult.objects.create(
                order=lab_order,
                hl7_obr_segment="MSH|^~\\&|LAB|HOSP|",
                resulted_by=lab_tech_user,
            )
        assert "OBR segment" in str(exc_info.value)

    def test_hl7_obx_validation(self, lab_order, lab_tech_user):
        """Test OBX segment validation."""
        lab_order.transition_to(OrderStatus.COLLECTED)

        # Invalid OBX (doesn't start with OBX|)
        with pytest.raises(DjangoValidationError) as exc_info:
            LabResult.objects.create(
                order=lab_order,
                hl7_obx_segments="PID|1||12345||DOE^JOHN||19800101",
                resulted_by=lab_tech_user,
            )
        assert "OBX segment" in str(exc_info.value)

    def test_parse_obx_values(self, lab_order, lab_tech_user):
        """Test parsing OBX segments."""
        lab_order.transition_to(OrderStatus.COLLECTED)

        obx_data = """OBX|1|NM|WBC^White Blood Cell Count||7.5|10*3/uL|4.5-11.0|N
OBX|2|NM|RBC^Red Blood Cell Count||4.8|10*6/uL|4.2-5.9|N
OBX|3|NM|HGB^Hemoglobin||14.5|g/dL|12.0-17.5|N"""

        result = LabResult.objects.create(
            order=lab_order,
            hl7_obx_segments=obx_data,
            resulted_by=lab_tech_user,
        )

        parsed = result.parse_obx_values()
        assert len(parsed) == 3
        assert parsed[0]["value"] == "7.5"
        assert parsed[0]["units"] == "10*3/uL"
        assert parsed[1]["identifier"] == "RBC^Red Blood Cell Count"


@pytest.mark.django_db
class TestLabOrderAPI:
    """Tests for lab order API endpoints."""

    def test_list_orders(self, authenticated_doctor_client, lab_order):
        """Test listing lab orders."""
        response = authenticated_doctor_client.get("/api/v1/lab/orders/")

        assert response.status_code == status.HTTP_200_OK

    def test_create_order(self, authenticated_doctor_client, sample_patient, test_type):
        """Test creating a lab order."""
        order_data = {
            "patient": str(sample_patient.id),
            "test_type": str(test_type.id),
            "priority": "URGENT",
            "clinical_notes": "Patient presenting with fatigue",
        }

        response = authenticated_doctor_client.post("/api/v1/lab/orders/", order_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["priority"] == "URGENT"
        assert LabOrder.objects.filter(patient=sample_patient).exists()

    def test_lab_tech_cannot_create_order(self, authenticated_lab_tech_client, sample_patient, test_type):
        """Test lab techs cannot create orders."""
        order_data = {
            "patient": str(sample_patient.id),
            "test_type": str(test_type.id),
        }

        response = authenticated_lab_tech_client.post("/api/v1/lab/orders/", order_data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_collect_specimen(self, authenticated_nurse_client, lab_order):
        """Test collecting specimen."""
        response = authenticated_nurse_client.post(f"/api/v1/lab/orders/{lab_order.id}/collect_specimen/")

        assert response.status_code == status.HTTP_200_OK
        lab_order.refresh_from_db()
        assert lab_order.status == OrderStatus.COLLECTED

    def test_cancel_order(self, authenticated_doctor_client, lab_order):
        """Test cancelling an order."""
        response = authenticated_doctor_client.post(f"/api/v1/lab/orders/{lab_order.id}/cancel/")

        assert response.status_code == status.HTTP_200_OK
        lab_order.refresh_from_db()
        assert lab_order.status == OrderStatus.CANCELLED

    def test_pending_results_endpoint(self, authenticated_lab_tech_client, lab_order):
        """Test pending results endpoint for lab techs."""
        lab_order.transition_to(OrderStatus.COLLECTED)

        response = authenticated_lab_tech_client.get("/api/v1/lab/orders/pending_results/")

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestLabResultAPI:
    """Tests for lab result API endpoints."""

    def test_create_result(self, authenticated_lab_tech_client, lab_order):
        """Test lab tech creating results."""
        lab_order.transition_to(OrderStatus.COLLECTED)

        result_data = {
            "order": str(lab_order.id),
            "hl7_obr_segment": "OBR|1|12345|67890|58410-2^CBC^LN|||20231115120000",
            "hl7_obx_segments": "OBX|1|NM|WBC||7.5|10*3/uL|4.5-11.0|N",
            "result_summary": "All values within normal limits",
            "is_abnormal": False,
            "is_critical": False,
        }

        response = authenticated_lab_tech_client.post("/api/v1/lab/results/", result_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Order should be updated to RESULTED
        lab_order.refresh_from_db()
        assert lab_order.status == OrderStatus.RESULTED

    def test_doctor_cannot_create_result(self, authenticated_doctor_client, lab_order):
        """Test doctors cannot create results."""
        lab_order.transition_to(OrderStatus.COLLECTED)

        result_data = {
            "order": str(lab_order.id),
            "hl7_obx_segments": "OBX|1|NM|WBC||7.5|10*3/uL|4.5-11.0|N",
        }

        response = authenticated_doctor_client.post("/api/v1/lab/results/", result_data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_review_result(self, authenticated_doctor_client, lab_order, lab_tech_user):
        """Test doctor reviewing results."""
        lab_order.transition_to(OrderStatus.COLLECTED)

        result = LabResult.objects.create(
            order=lab_order,
            hl7_obx_segments="OBX|1|NM|WBC||7.5|10*3/uL|4.5-11.0|N",
            result_summary="Normal",
            resulted_by=lab_tech_user,
        )
        lab_order.status = OrderStatus.RESULTED
        lab_order.save()

        response = authenticated_doctor_client.post(
            f"/api/v1/lab/results/{result.id}/review/",
            {"review_notes": "Results reviewed, no action needed"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        result.refresh_from_db()
        assert result.reviewed_by is not None
        assert result.review_notes == "Results reviewed, no action needed"

        lab_order.refresh_from_db()
        assert lab_order.status == OrderStatus.REVIEWED

    def test_critical_results_endpoint(self, authenticated_doctor_client, lab_order, lab_tech_user):
        """Test critical results endpoint."""
        lab_order.transition_to(OrderStatus.COLLECTED)

        LabResult.objects.create(
            order=lab_order,
            hl7_obx_segments="OBX|1|NM|K||6.5|mmol/L|3.5-5.0|H",
            result_summary="CRITICAL: Potassium elevated",
            is_critical=True,
            resulted_by=lab_tech_user,
        )

        response = authenticated_doctor_client.get("/api/v1/lab/results/critical/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1


@pytest.mark.django_db
class TestTestTypeAPI:
    """Tests for test type API endpoints."""

    def test_list_test_types(self, authenticated_doctor_client, test_type):
        """Test listing test types."""
        response = authenticated_doctor_client.get("/api/v1/lab/test-types/")

        assert response.status_code == status.HTTP_200_OK

    def test_create_test_type_admin_only(self, authenticated_admin_client, authenticated_doctor_client):
        """Test only admins can create test types."""
        test_data = {
            "code": "UA",
            "name": "Urinalysis",
            "category": "URINALYSIS",
            "specimen_type": "Urine",
            "turnaround_hours": 2,
        }

        # Admin can create
        admin_response = authenticated_admin_client.post("/api/v1/lab/test-types/", test_data, format="json")
        assert admin_response.status_code == status.HTTP_201_CREATED

        # Doctor cannot create
        test_data["code"] = "UA2"
        doctor_response = authenticated_doctor_client.post("/api/v1/lab/test-types/", test_data, format="json")
        assert doctor_response.status_code == status.HTTP_403_FORBIDDEN
