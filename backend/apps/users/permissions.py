"""
Role-based permission classes for Hospital Backend.

These permissions work with DRF's permission system to enforce
role-based access control across the API.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from rest_framework.permissions import BasePermission
from .models import UserRole


class IsAdmin(BasePermission):
    """
    Allow access only to administrators.
    """
    message = 'Admin access required.'
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_admin
        )


class IsDoctor(BasePermission):
    """
    Allow access only to doctors.
    """
    message = 'Doctor access required.'
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_doctor
        )


class IsNurse(BasePermission):
    """
    Allow access only to nurses.
    """
    message = 'Nurse access required.'
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_nurse
        )


class IsLabTech(BasePermission):
    """
    Allow access only to lab technicians.
    """
    message = 'Lab technician access required.'
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_lab_tech
        )


class IsReceptionist(BasePermission):
    """
    Allow access only to receptionists.
    """
    message = 'Receptionist access required.'
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_receptionist
        )


class IsClinicalStaff(BasePermission):
    """
    Allow access to clinical staff (doctors, nurses, lab techs).
    """
    message = 'Clinical staff access required.'
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_clinical_staff
        )


class IsAdminOrDoctor(BasePermission):
    """
    Allow access to administrators or doctors.
    """
    message = 'Admin or doctor access required.'
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_admin or request.user.is_doctor)
        )


class IsAdminOrClinicalStaff(BasePermission):
    """
    Allow access to administrators or clinical staff.
    """
    message = 'Admin or clinical staff access required.'
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_admin or request.user.is_clinical_staff)
        )


class CanOrderLabs(BasePermission):
    """
    Allow access to users who can create lab orders.
    """
    message = 'Lab ordering permission required.'
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.can_order_labs
        )


class CanViewPatients(BasePermission):
    """
    Allow access to users who can view patient records.
    """
    message = 'Patient viewing permission required.'
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.can_view_patients
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission to only allow owners or admins to edit an object.
    """
    message = 'You do not have permission to perform this action.'
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_admin:
            return True
        
        # Check if the object has a user field and it matches
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if the object IS a user and it matches
        if hasattr(obj, 'email'):
            return obj == request.user
        
        return False


class ReadOnly(BasePermission):
    """
    Allow read-only access (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        return request.method in ['GET', 'HEAD', 'OPTIONS']
