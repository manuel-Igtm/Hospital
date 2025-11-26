#!/usr/bin/env python
"""
Seed script for demo data.

Creates demo users with different roles for testing and development.

Usage:
    python manage.py shell < scripts/seed_demo_data.py

    Or run directly:
    cd backend && python scripts/seed_demo_data.py

© 2025 Immanuel Njogu. All rights reserved.
"""

import os
import sys
from pathlib import Path

# Add backend to path if running directly
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django

django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

# Import Patient model
from apps.patients.models import BloodType, Gender, Patient

# Import Lab Orders models
from apps.lab_orders.models import TestCategory, TestType

# Demo users configuration
DEMO_USERS = [
    {
        "email": "admin@hospital.local",
        "password": "admin123!",
        "first_name": "System",
        "last_name": "Administrator",
        "role": "ADMIN",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "email": "dr.smith@hospital.local",
        "password": "doctor123!",
        "first_name": "John",
        "last_name": "Smith",
        "role": "DOCTOR",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "nurse.jane@hospital.local",
        "password": "nurse123!",
        "first_name": "Jane",
        "last_name": "Doe",
        "role": "NURSE",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "lab.tech@hospital.local",
        "password": "lab123!",
        "first_name": "Mike",
        "last_name": "Johnson",
        "role": "LAB_TECH",
        "is_staff": False,
        "is_superuser": False,
    },
]


def create_demo_users() -> None:
    """Create demo users if they don't exist."""
    print("Creating demo users...")

    created_count = 0
    skipped_count = 0

    with transaction.atomic():
        for user_data in DEMO_USERS:
            email = user_data["email"]
            password = user_data.pop("password")

            user, created = User.objects.get_or_create(
                email=email,
                defaults=user_data,
            )

            if created:
                user.set_password(password)
                user.save()
                print(f"  ✓ Created: {email} ({user_data['role']})")
                created_count += 1
            else:
                print(f"  - Skipped (exists): {email}")
                skipped_count += 1

    print(f"\nSummary: {created_count} created, {skipped_count} skipped")


def print_credentials() -> None:
    """Print demo user credentials."""
    print("\n" + "=" * 60)
    print("Demo User Credentials")
    print("=" * 60)
    print(f"{'Email':<30} {'Password':<15} {'Role':<15}")
    print("-" * 60)
    for user in DEMO_USERS:
        print(f"{user['email']:<30} {user.get('password', 'N/A'):<15} {user['role']:<15}")
    print("=" * 60)
    print("\nWARNING: These are demo credentials. Do NOT use in production!")


# Demo patients configuration
DEMO_PATIENTS = [
    {
        "first_name": "Alice",
        "last_name": "Johnson",
        "middle_name": "Marie",
        "date_of_birth": "1985-03-15",
        "gender": Gender.FEMALE,
        "phone": "+15551234567",
        "email": "alice.johnson@email.com",
        "address_line1": "123 Oak Street",
        "city": "Springfield",
        "state": "IL",
        "postal_code": "62701",
        "country": "USA",
        "blood_type": BloodType.A_POS,
        "allergies": "Penicillin, Shellfish",
        "emergency_contact_name": "Bob Johnson",
        "emergency_contact_phone": "+15559876543",
        "emergency_contact_relationship": "Spouse",
    },
    {
        "first_name": "Robert",
        "last_name": "Williams",
        "date_of_birth": "1972-08-22",
        "gender": Gender.MALE,
        "phone": "+15552345678",
        "email": "robert.williams@email.com",
        "address_line1": "456 Maple Avenue",
        "address_line2": "Apt 3B",
        "city": "Chicago",
        "state": "IL",
        "postal_code": "60601",
        "country": "USA",
        "blood_type": BloodType.O_NEG,
        "allergies": "",
        "emergency_contact_name": "Susan Williams",
        "emergency_contact_phone": "+15558765432",
        "emergency_contact_relationship": "Sister",
    },
    {
        "first_name": "Maria",
        "last_name": "Garcia",
        "middle_name": "Elena",
        "date_of_birth": "1990-12-01",
        "gender": Gender.FEMALE,
        "phone": "+15553456789",
        "email": "maria.garcia@email.com",
        "address_line1": "789 Pine Road",
        "city": "Naperville",
        "state": "IL",
        "postal_code": "60540",
        "country": "USA",
        "blood_type": BloodType.B_POS,
        "allergies": "Latex, Ibuprofen",
        "emergency_contact_name": "Carlos Garcia",
        "emergency_contact_phone": "+15557654321",
        "emergency_contact_relationship": "Brother",
    },
    {
        "first_name": "James",
        "last_name": "Brown",
        "date_of_birth": "1958-05-10",
        "gender": Gender.MALE,
        "phone": "+15554567890",
        "email": "james.brown@email.com",
        "address_line1": "321 Elm Court",
        "city": "Evanston",
        "state": "IL",
        "postal_code": "60201",
        "country": "USA",
        "blood_type": BloodType.AB_POS,
        "allergies": "Sulfa drugs",
        "emergency_contact_name": "Patricia Brown",
        "emergency_contact_phone": "+15556543210",
        "emergency_contact_relationship": "Wife",
    },
    {
        "first_name": "Emily",
        "last_name": "Davis",
        "middle_name": "Rose",
        "date_of_birth": "2005-07-20",
        "gender": Gender.FEMALE,
        "phone": "+15555678901",
        "email": "emily.davis@email.com",
        "address_line1": "654 Cedar Lane",
        "city": "Oak Park",
        "state": "IL",
        "postal_code": "60301",
        "country": "USA",
        "blood_type": BloodType.A_NEG,
        "allergies": "",
        "emergency_contact_name": "Michael Davis",
        "emergency_contact_phone": "+15554321098",
        "emergency_contact_relationship": "Father",
    },
]


def create_demo_patients() -> None:
    """Create demo patients if they don't exist."""
    from datetime import datetime

    print("\nCreating demo patients...")

    created_count = 0
    skipped_count = 0

    with transaction.atomic():
        for patient_data in DEMO_PATIENTS:
            # Convert date string to date object
            dob_str = patient_data.pop("date_of_birth")
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()

            # Check if patient already exists (by name and DOB)
            existing = Patient.objects.filter(
                first_name=patient_data["first_name"],
                last_name=patient_data["last_name"],
                date_of_birth=dob,
            ).first()

            if existing:
                print(f"  - Skipped (exists): {patient_data['first_name']} {patient_data['last_name']}")
                skipped_count += 1
                # Restore for next run
                patient_data["date_of_birth"] = dob_str
                continue

            patient = Patient.objects.create(
                date_of_birth=dob,
                **patient_data,
            )
            print(f"  ✓ Created: {patient.full_name} (MRN: {patient.mrn})")
            created_count += 1

            # Restore for next run
            patient_data["date_of_birth"] = dob_str

    print(f"\nSummary: {created_count} created, {skipped_count} skipped")


# Demo test types configuration
DEMO_TEST_TYPES = [
    {
        "code": "CBC",
        "name": "Complete Blood Count",
        "description": "Measures red blood cells, white blood cells, hemoglobin, hematocrit, and platelets",
        "category": TestCategory.HEMATOLOGY,
        "loinc_code": "58410-2",
        "specimen_type": "Blood",
        "turnaround_hours": 4,
    },
    {
        "code": "BMP",
        "name": "Basic Metabolic Panel",
        "description": "Measures glucose, calcium, electrolytes, and kidney function",
        "category": TestCategory.CHEMISTRY,
        "loinc_code": "51990-0",
        "specimen_type": "Blood",
        "turnaround_hours": 4,
    },
    {
        "code": "CMP",
        "name": "Comprehensive Metabolic Panel",
        "description": "BMP plus liver function tests",
        "category": TestCategory.CHEMISTRY,
        "loinc_code": "24323-8",
        "specimen_type": "Blood",
        "turnaround_hours": 6,
    },
    {
        "code": "LFT",
        "name": "Liver Function Tests",
        "description": "Measures liver enzymes and bilirubin",
        "category": TestCategory.CHEMISTRY,
        "loinc_code": "24325-3",
        "specimen_type": "Blood",
        "turnaround_hours": 6,
    },
    {
        "code": "UA",
        "name": "Urinalysis",
        "description": "Analyzes urine for various substances and cells",
        "category": TestCategory.URINALYSIS,
        "loinc_code": "24356-8",
        "specimen_type": "Urine",
        "turnaround_hours": 2,
    },
    {
        "code": "TSH",
        "name": "Thyroid Stimulating Hormone",
        "description": "Measures thyroid function",
        "category": TestCategory.CHEMISTRY,
        "loinc_code": "3016-3",
        "specimen_type": "Blood",
        "turnaround_hours": 24,
    },
    {
        "code": "LIPID",
        "name": "Lipid Panel",
        "description": "Measures cholesterol and triglycerides",
        "category": TestCategory.CHEMISTRY,
        "loinc_code": "24331-1",
        "specimen_type": "Blood",
        "turnaround_hours": 6,
    },
    {
        "code": "HBA1C",
        "name": "Hemoglobin A1c",
        "description": "Measures average blood sugar over 2-3 months",
        "category": TestCategory.CHEMISTRY,
        "loinc_code": "4548-4",
        "specimen_type": "Blood",
        "turnaround_hours": 24,
    },
]


def create_demo_test_types() -> None:
    """Create demo test types if they don't exist."""
    print("\nCreating demo test types...")

    created_count = 0
    skipped_count = 0

    with transaction.atomic():
        for test_data in DEMO_TEST_TYPES:
            code = test_data["code"]

            test_type, created = TestType.objects.get_or_create(
                code=code,
                defaults=test_data,
            )

            if created:
                print(f"  ✓ Created: {code} - {test_data['name']}")
                created_count += 1
            else:
                print(f"  - Skipped (exists): {code}")
                skipped_count += 1

    print(f"\nSummary: {created_count} created, {skipped_count} skipped")


if __name__ == "__main__":
    # Re-add passwords for credential display (they were popped during creation)
    DEMO_USERS[0]["password"] = "admin123!"
    DEMO_USERS[1]["password"] = "doctor123!"
    DEMO_USERS[2]["password"] = "nurse123!"
    DEMO_USERS[3]["password"] = "lab123!"

    print_credentials()
    print()
    create_demo_users()
    create_demo_patients()
    create_demo_test_types()
