"""Admin configuration for lab_orders app."""

from django.contrib import admin

from .models import LabOrder, LabResult, TestType


@admin.register(TestType)
class TestTypeAdmin(admin.ModelAdmin):
    """Admin configuration for TestType model."""

    list_display = ["code", "name", "category", "specimen_type", "turnaround_hours", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["code", "name", "loinc_code"]
    ordering = ["category", "code"]


@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    """Admin configuration for LabOrder model."""

    list_display = ["order_number", "patient", "test_type", "ordering_provider", "priority", "status", "ordered_at"]
    list_filter = ["status", "priority", "test_type__category", "ordered_at"]
    search_fields = ["order_number", "patient__mrn", "patient__last_name"]
    ordering = ["-ordered_at"]
    readonly_fields = ["id", "order_number", "ordered_at", "updated_at"]

    fieldsets = (
        ("Order Information", {"fields": ("id", "order_number", "patient", "test_type", "ordering_provider")}),
        ("Details", {"fields": ("priority", "clinical_notes", "status")}),
        ("Specimen", {"fields": ("specimen_collected_at", "specimen_collected_by")}),
        ("Timestamps", {"fields": ("ordered_at", "updated_at")}),
    )


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    """Admin configuration for LabResult model."""

    list_display = ["order", "is_abnormal", "is_critical", "resulted_by", "resulted_at", "reviewed_by", "reviewed_at"]
    list_filter = ["is_abnormal", "is_critical", "resulted_at"]
    search_fields = ["order__order_number", "order__patient__mrn"]
    ordering = ["-resulted_at"]
    readonly_fields = ["id", "resulted_at", "reviewed_at"]
