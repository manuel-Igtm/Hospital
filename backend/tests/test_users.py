"""
Tests for the users app.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from apps.users.models import User, UserRole


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model."""
    
    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
        )
        
        assert user.email == 'test@example.com'
        assert user.check_password('TestPass123!')
        assert user.role == UserRole.RECEPTIONIST  # default role
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = User.objects.create_superuser(
            email='super@example.com',
            password='SuperPass123!',
            first_name='Super',
            last_name='Admin',
        )
        
        assert superuser.is_staff
        assert superuser.is_superuser
        assert superuser.role == UserRole.ADMIN
    
    def test_full_name(self):
        """Test full_name property."""
        user = User(first_name='John', last_name='Doe')
        assert user.full_name == 'John Doe'
    
    def test_role_checks(self):
        """Test role check properties."""
        admin = User(role=UserRole.ADMIN)
        doctor = User(role=UserRole.DOCTOR)
        nurse = User(role=UserRole.NURSE)
        lab_tech = User(role=UserRole.LAB_TECH)
        
        assert admin.is_admin
        assert doctor.is_doctor
        assert nurse.is_nurse
        assert lab_tech.is_lab_tech
        
        assert doctor.is_clinical_staff
        assert nurse.is_clinical_staff
        assert lab_tech.is_clinical_staff
        assert not admin.is_clinical_staff
    
    def test_can_order_labs(self):
        """Test lab ordering permission property."""
        doctor = User(role=UserRole.DOCTOR)
        nurse = User(role=UserRole.NURSE)
        lab_tech = User(role=UserRole.LAB_TECH)
        receptionist = User(role=UserRole.RECEPTIONIST)
        
        assert doctor.can_order_labs
        assert nurse.can_order_labs
        assert not lab_tech.can_order_labs
        assert not receptionist.can_order_labs


@pytest.mark.django_db
class TestAuthEndpoints:
    """Tests for authentication endpoints."""
    
    def test_login_success(self, api_client, admin_user):
        """Test successful login."""
        response = api_client.post(
            '/api/v1/auth/login/',
            {'email': 'admin@hospital.test', 'password': 'AdminPass123!'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == 'admin@hospital.test'
        assert response.data['user']['role'] == 'ADMIN'
    
    def test_login_invalid_credentials(self, api_client, admin_user):
        """Test login with wrong password."""
        response = api_client.post(
            '/api/v1/auth/login/',
            {'email': 'admin@hospital.test', 'password': 'wrongpassword'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_me_endpoint(self, authenticated_admin_client, admin_user):
        """Test retrieving current user."""
        response = authenticated_admin_client.get('/api/v1/auth/me/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == admin_user.email
        assert response.data['role'] == UserRole.ADMIN
    
    def test_me_unauthenticated(self, api_client):
        """Test me endpoint without authentication."""
        response = api_client.get('/api/v1/auth/me/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout(self, authenticated_admin_client, admin_user, api_client):
        """Test logout (token blacklist)."""
        # First login to get tokens
        login_response = api_client.post(
            '/api/v1/auth/login/',
            {'email': 'admin@hospital.test', 'password': 'AdminPass123!'},
            format='json'
        )
        refresh_token = login_response.data['refresh']
        
        # Logout
        response = authenticated_admin_client.post(
            '/api/v1/auth/logout/',
            {'refresh': refresh_token},
            format='json'
        )
        
        assert response.status_code == status.HTTP_205_RESET_CONTENT


@pytest.mark.django_db
class TestUserViewSet:
    """Tests for user management endpoints."""
    
    def test_list_users_admin_only(self, authenticated_admin_client, authenticated_doctor_client):
        """Test that only admins can list users."""
        admin_response = authenticated_admin_client.get('/api/v1/users/')
        doctor_response = authenticated_doctor_client.get('/api/v1/users/')
        
        assert admin_response.status_code == status.HTTP_200_OK
        assert doctor_response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_user_admin_only(self, authenticated_admin_client, authenticated_doctor_client):
        """Test that only admins can create users."""
        user_data = {
            'email': 'new@hospital.test',
            'password': 'NewPass123!',
            'password_confirm': 'NewPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'DOCTOR',
        }
        
        admin_response = authenticated_admin_client.post(
            '/api/v1/users/',
            user_data,
            format='json'
        )
        
        assert admin_response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='new@hospital.test').exists()
    
    def test_deactivate_user(self, authenticated_admin_client, doctor_user):
        """Test deactivating a user (soft delete)."""
        response = authenticated_admin_client.delete(
            f'/api/v1/users/{doctor_user.id}/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        doctor_user.refresh_from_db()
        assert not doctor_user.is_active
    
    def test_cannot_deactivate_self(self, authenticated_admin_client, admin_user):
        """Test that users cannot deactivate themselves."""
        response = authenticated_admin_client.delete(
            f'/api/v1/users/{admin_user.id}/'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPermissions:
    """Tests for role-based permissions."""
    
    def test_admin_can_access_admin_routes(self, authenticated_admin_client):
        """Test admin access to admin-only routes."""
        response = authenticated_admin_client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_doctor_cannot_access_admin_routes(self, authenticated_doctor_client):
        """Test doctor denied access to admin-only routes."""
        response = authenticated_doctor_client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
