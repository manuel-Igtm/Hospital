"""Admin configuration for patients app."""

from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Admin configuration for Patient model."""
    
    list_display = ['mrn', 'full_name', 'date_of_birth', 'gender', 'phone', 'is_active']
    list_filter = ['gender', 'blood_type', 'is_active', 'state', 'created_at']
    search_fields = ['mrn', 'first_name', 'last_name', 'email', 'phone']
    ordering = ['last_name', 'first_name']
    readonly_fields = ['id', 'mrn', 'ssn_masked', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'mrn', 'ssn_masked')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender')
        }),
        ('Contact', {
            'fields': ('phone', 'email')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Medical', {
            'fields': ('blood_type', 'allergies')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
