"""
Pytest configuration and fixtures for Hospital Backend tests.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

import pytest
from rest_framework.test import APIClient
from apps.users.models import User, UserRole


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def admin_user(db):
    """Create and return an admin user."""
    return User.objects.create_user(
        email='admin@hospital.test',
        password='AdminPass123!',
        first_name='Admin',
        last_name='User',
        role=UserRole.ADMIN,
        is_staff=True,
    )


@pytest.fixture
def doctor_user(db):
    """Create and return a doctor user."""
    return User.objects.create_user(
        email='doctor@hospital.test',
        password='DoctorPass123!',
        first_name='John',
        last_name='Doctor',
        role=UserRole.DOCTOR,
        license_number='MD12345',
        department='Internal Medicine',
    )


@pytest.fixture
def nurse_user(db):
    """Create and return a nurse user."""
    return User.objects.create_user(
        email='nurse@hospital.test',
        password='NursePass123!',
        first_name='Jane',
        last_name='Nurse',
        role=UserRole.NURSE,
        license_number='RN67890',
        department='Emergency',
    )


@pytest.fixture
def lab_tech_user(db):
    """Create and return a lab technician user."""
    return User.objects.create_user(
        email='labtech@hospital.test',
        password='LabTechPass123!',
        first_name='Lab',
        last_name='Technician',
        role=UserRole.LAB_TECH,
        department='Laboratory',
    )


@pytest.fixture
def receptionist_user(db):
    """Create and return a receptionist user."""
    return User.objects.create_user(
        email='receptionist@hospital.test',
        password='ReceptionPass123!',
        first_name='Front',
        last_name='Desk',
        role=UserRole.RECEPTIONIST,
    )


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    """Return an API client authenticated as admin."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def authenticated_doctor_client(api_client, doctor_user):
    """Return an API client authenticated as doctor."""
    api_client.force_authenticate(user=doctor_user)
    return api_client


@pytest.fixture
def authenticated_nurse_client(api_client, nurse_user):
    """Return an API client authenticated as nurse."""
    api_client.force_authenticate(user=nurse_user)
    return api_client


@pytest.fixture
def authenticated_lab_tech_client(api_client, lab_tech_user):
    """Return an API client authenticated as lab tech."""
    api_client.force_authenticate(user=lab_tech_user)
    return api_client
