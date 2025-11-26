"""
Tests for the patients app.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from datetime import date

from django.conf import settings

import pytest

from apps.patients.models import BloodType, Gender, Patient


# Set a test encryption key
@pytest.fixture(autouse=True)
def set_encryption_key(settings):
    """Set PII encryption key for tests."""
    settings.HOSPITAL_SETTINGS = {
        "ENABLE_C_MODULES": False,
        "PII_ENCRYPTION_KEY": "test-encryption-key-for-pytest-12345",
    }


@pytest.fixture
def sample_patient(db):
    """Create a sample patient."""
    patient = Patient(
        first_name="John",
        last_name="Doe",
        middle_name="William",
        date_of_birth=date(1980, 5, 15),
        gender=Gender.MALE,
        phone="+15551234567",
        email="johndoe@example.com",
        address_line1="123 Main St",
        city="Springfield",
        state="IL",
        postal_code="62701",
        blood_type=BloodType.A_POS,
    )
    patient.set_ssn("123-45-6789")
    patient.save()
    return patient


@pytest.mark.django_db
class TestPatientModel:
    """Tests for Patient model."""

    def test_create_patient(self, sample_patient):
        """Test creating a patient."""
        assert sample_patient.pk is not None
        assert sample_patient.mrn.startswith("MRN-")
        assert sample_patient.full_name == "John William Doe"

    def test_patient_age(self):
        """Test age calculation."""
        # Create patient born 30 years ago
        from datetime import date

        today = date.today()
        birth_date = date(today.year - 30, today.month, today.day)

        patient = Patient(date_of_birth=birth_date)
        assert patient.age == 30

    def test_ssn_encryption(self, sample_patient):
        """Test SSN is encrypted and can be decrypted."""
        # Get the decrypted SSN
        decrypted = sample_patient.get_ssn()
        assert decrypted == "123456789"  # without dashes

        # Verify it's stored encrypted (not plain text)
        assert sample_patient._ssn_encrypted is not None
        assert b"123456789" not in bytes(sample_patient._ssn_encrypted)

    def test_ssn_masked(self, sample_patient):
        """Test masked SSN display."""
        assert sample_patient.ssn_masked == "XXX-XX-6789"

    def test_find_by_ssn(self, sample_patient):
        """Test finding patient by SSN."""
        # Find with dashes
        found = Patient.find_by_ssn("123-45-6789")
        assert found is not None
        assert found.id == sample_patient.id

        # Find without dashes
        found = Patient.find_by_ssn("123456789")
        assert found is not None
        assert found.id == sample_patient.id

        # Not found
        not_found = Patient.find_by_ssn("999-99-9999")
        assert not_found is None

    def test_mrn_uniqueness(self, db):
        """Test MRN is unique."""
        patient1 = Patient.objects.create(
            first_name="Patient",
            last_name="One",
            date_of_birth=date(1990, 1, 1),
        )
        patient2 = Patient.objects.create(
            first_name="Patient",
            last_name="Two",
            date_of_birth=date(1990, 1, 1),
        )

        assert patient1.mrn != patient2.mrn


@pytest.mark.django_db
class TestPatientAPI:
    """Tests for patient API endpoints."""

    def test_list_patients(self, authenticated_doctor_client, sample_patient):
        """Test listing patients."""
        response = authenticated_doctor_client.get("/api/v1/patients/")

        assert response.status_code == 200
        assert len(response.data["results"]) >= 1

    def test_create_patient(self, authenticated_doctor_client):
        """Test creating a patient via API."""
        patient_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": "1985-03-20",
            "gender": "F",
            "ssn": "987-65-4321",
            "phone": "+15559876543",
            "email": "janesmith@example.com",
        }

        response = authenticated_doctor_client.post("/api/v1/patients/", patient_data, format="json")

        assert response.status_code == 201
        assert response.data["first_name"] == "Jane"
        assert response.data["mrn"].startswith("MRN-")

        # Verify SSN is encrypted
        patient = Patient.objects.get(id=response.data["id"])
        assert patient.get_ssn() == "987654321"

    def test_retrieve_patient(self, authenticated_doctor_client, sample_patient):
        """Test retrieving a single patient."""
        response = authenticated_doctor_client.get(f"/api/v1/patients/{sample_patient.id}/")

        assert response.status_code == 200
        assert response.data["mrn"] == sample_patient.mrn
        assert "ssn_masked" in response.data
        assert response.data["ssn_masked"] == "XXX-XX-6789"

    def test_update_patient(self, authenticated_doctor_client, sample_patient):
        """Test updating a patient."""
        response = authenticated_doctor_client.patch(
            f"/api/v1/patients/{sample_patient.id}/", {"phone": "+15559999999"}, format="json"
        )

        assert response.status_code == 200
        sample_patient.refresh_from_db()
        assert sample_patient.phone == "+15559999999"

    def test_search_patients(self, authenticated_doctor_client, sample_patient):
        """Test searching patients."""
        response = authenticated_doctor_client.get("/api/v1/patients/", {"search": "Doe"})

        assert response.status_code == 200
        assert len(response.data["results"]) >= 1

    def test_find_by_ssn_endpoint(self, authenticated_doctor_client, sample_patient):
        """Test find by SSN endpoint."""
        response = authenticated_doctor_client.get("/api/v1/patients/find_by_ssn/", {"ssn": "123-45-6789"})

        assert response.status_code == 200
        assert response.data["mrn"] == sample_patient.mrn

    def test_deactivate_patient_admin_only(
        self, authenticated_admin_client, authenticated_doctor_client, sample_patient
    ):
        """Test only admins can deactivate patients."""
        # Doctor cannot deactivate
        doctor_response = authenticated_doctor_client.delete(f"/api/v1/patients/{sample_patient.id}/")
        assert doctor_response.status_code == 403

        # Admin can deactivate
        admin_response = authenticated_admin_client.delete(f"/api/v1/patients/{sample_patient.id}/")
        assert admin_response.status_code == 200

        sample_patient.refresh_from_db()
        assert not sample_patient.is_active

    def test_duplicate_ssn_rejected(self, authenticated_doctor_client, sample_patient):
        """Test that duplicate SSN is rejected."""
        patient_data = {
            "first_name": "Duplicate",
            "last_name": "Patient",
            "date_of_birth": "1990-01-01",
            "ssn": "123-45-6789",  # Same as sample_patient
        }

        response = authenticated_doctor_client.post("/api/v1/patients/", patient_data, format="json")

        assert response.status_code == 400
        # Error may be in 'ssn' field or in 'errors.ssn' depending on exception handler
        assert "ssn" in response.data or ("errors" in response.data and "ssn" in response.data["errors"])


@pytest.mark.django_db
class TestPatientPermissions:
    """Tests for patient-related permissions."""

    def test_receptionist_can_view_patients(self, api_client, receptionist_user, sample_patient):
        """Test receptionists can view patients."""
        api_client.force_authenticate(user=receptionist_user)

        response = api_client.get("/api/v1/patients/")
        assert response.status_code == 200

    def test_receptionist_cannot_create_patients(self, api_client, receptionist_user):
        """Test receptionists cannot create patients."""
        api_client.force_authenticate(user=receptionist_user)

        response = api_client.post(
            "/api/v1/patients/",
            {"first_name": "Test", "last_name": "Patient", "date_of_birth": "1990-01-01"},
            format="json",
        )

        assert response.status_code == 403

    def test_lab_tech_can_view_patients(self, authenticated_lab_tech_client, sample_patient):
        """Test lab techs can view patients."""
        response = authenticated_lab_tech_client.get("/api/v1/patients/")
        assert response.status_code == 200
