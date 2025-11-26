"""
Custom User model with role-based access control.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator
import uuid


class UserRole(models.TextChoices):
    """User role choices for RBAC."""
    ADMIN = 'ADMIN', 'Administrator'
    DOCTOR = 'DOCTOR', 'Doctor'
    NURSE = 'NURSE', 'Nurse'
    LAB_TECH = 'LAB_TECH', 'Lab Technician'
    RECEPTIONIST = 'RECEPTIONIST', 'Receptionist'


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user."""
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using email for authentication.
    
    Supports role-based access control with predefined roles:
    - ADMIN: Full system access
    - DOCTOR: Patient care, order creation
    - NURSE: Patient care, limited ordering
    - LAB_TECH: Lab result management
    - RECEPTIONIST: Scheduling, patient registration
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text='Unique identifier for the user'
    )
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text='Email address (used for login)'
    )
    first_name = models.CharField(
        max_length=150,
        help_text='First name'
    )
    last_name = models.CharField(
        max_length=150,
        help_text='Last name'
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.RECEPTIONIST,
        db_index=True,
        help_text='User role for access control'
    )
    
    # Professional info (optional, for clinical staff)
    license_number = models.CharField(
        max_length=50,
        blank=True,
        help_text='Professional license number'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text='Department or specialty'
    )
    
    # Status fields
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the user can log in'
    )
    is_staff = models.BooleanField(
        default=False,
        help_text='Whether user can access admin site'
    )
    
    # Timestamps
    date_joined = models.DateTimeField(
        default=timezone.now,
        help_text='Date and time when user was created'
    )
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last login timestamp'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f'{self.full_name} ({self.email})'
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return f'{self.first_name} {self.last_name}'.strip()
    
    # Role check properties
    @property
    def is_admin(self):
        """Check if user is an administrator."""
        return self.role == UserRole.ADMIN or self.is_superuser
    
    @property
    def is_doctor(self):
        """Check if user is a doctor."""
        return self.role == UserRole.DOCTOR
    
    @property
    def is_nurse(self):
        """Check if user is a nurse."""
        return self.role == UserRole.NURSE
    
    @property
    def is_lab_tech(self):
        """Check if user is a lab technician."""
        return self.role == UserRole.LAB_TECH
    
    @property
    def is_receptionist(self):
        """Check if user is a receptionist."""
        return self.role == UserRole.RECEPTIONIST
    
    @property
    def is_clinical_staff(self):
        """Check if user is clinical staff (doctor, nurse, lab tech)."""
        return self.role in [UserRole.DOCTOR, UserRole.NURSE, UserRole.LAB_TECH]
    
    @property
    def can_order_labs(self):
        """Check if user can create lab orders."""
        return self.role in [UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE]
    
    @property
    def can_view_patients(self):
        """Check if user can view patient records."""
        return self.role in [
            UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE, 
            UserRole.LAB_TECH, UserRole.RECEPTIONIST
        ]
