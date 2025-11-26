"""
Patient serializers for API endpoints.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from rest_framework import serializers
from .models import Patient, Gender, BloodType


class PatientListSerializer(serializers.ModelSerializer):
    """
    Serializer for patient list view (limited fields).
    """
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'mrn', 'full_name', 'first_name', 'last_name',
            'date_of_birth', 'age', 'gender', 'phone', 'is_active'
        ]


class PatientDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for patient detail view (all fields except encrypted SSN).
    """
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    ssn_masked = serializers.CharField(read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'mrn', 'full_name', 'first_name', 'last_name', 'middle_name',
            'date_of_birth', 'age', 'gender', 'ssn_masked',
            'phone', 'email',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'blood_type', 'allergies',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'mrn', 'created_at', 'updated_at']


class PatientCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new patients.
    """
    ssn = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text='Social Security Number (will be encrypted)'
    )
    
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'middle_name',
            'date_of_birth', 'gender', 'ssn',
            'phone', 'email',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'blood_type', 'allergies',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
        ]
    
    def validate_ssn(self, value):
        """Validate SSN format and uniqueness."""
        if not value:
            return value
        
        # Remove formatting
        ssn_clean = value.replace('-', '').replace(' ', '')
        
        # Validate format (9 digits)
        if not ssn_clean.isdigit() or len(ssn_clean) != 9:
            raise serializers.ValidationError(
                'SSN must be 9 digits (format: XXX-XX-XXXX or XXXXXXXXX)'
            )
        
        # Check uniqueness via hash
        existing = Patient.find_by_ssn(value)
        if existing:
            raise serializers.ValidationError('A patient with this SSN already exists.')
        
        return value
    
    def create(self, validated_data):
        """Create patient with encrypted SSN."""
        ssn = validated_data.pop('ssn', None)
        patient = Patient(**validated_data)
        
        if ssn:
            patient.set_ssn(ssn)
        
        patient.save()
        return patient


class PatientUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing patients.
    """
    ssn = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text='New SSN (will be encrypted). Leave blank to keep existing.'
    )
    
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'middle_name',
            'date_of_birth', 'gender', 'ssn',
            'phone', 'email',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'blood_type', 'allergies',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'is_active',
        ]
    
    def validate_ssn(self, value):
        """Validate SSN format and uniqueness for updates."""
        if not value:
            return value
        
        # Remove formatting
        ssn_clean = value.replace('-', '').replace(' ', '')
        
        # Validate format
        if not ssn_clean.isdigit() or len(ssn_clean) != 9:
            raise serializers.ValidationError(
                'SSN must be 9 digits (format: XXX-XX-XXXX or XXXXXXXXX)'
            )
        
        # Check uniqueness (excluding current patient)
        existing = Patient.find_by_ssn(value)
        if existing and existing.id != self.instance.id:
            raise serializers.ValidationError('A patient with this SSN already exists.')
        
        return value
    
    def update(self, instance, validated_data):
        """Update patient with optional SSN change."""
        ssn = validated_data.pop('ssn', None)
        
        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update SSN if provided
        if ssn:
            instance.set_ssn(ssn)
        
        instance.save()
        return instance


class PatientSearchSerializer(serializers.Serializer):
    """
    Serializer for patient search parameters.
    """
    mrn = serializers.CharField(required=False)
    name = serializers.CharField(required=False, help_text='Search in first/last name')
    date_of_birth = serializers.DateField(required=False)
    ssn = serializers.CharField(required=False, write_only=True, help_text='Exact SSN match')
