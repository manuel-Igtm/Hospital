"""
Patient views and viewsets.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view

from apps.users.permissions import (
    CanViewPatients,
    IsAdmin,
    IsAdminOrClinicalStaff,
)

from .models import Patient
from .serializers import (
    PatientCreateSerializer,
    PatientDetailSerializer,
    PatientListSerializer,
    PatientUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["patients"],
        description="List all patients",
        parameters=[
            OpenApiParameter(name="search", description="Search in name, MRN"),
            OpenApiParameter(name="gender", description="Filter by gender"),
            OpenApiParameter(name="is_active", description="Filter by active status"),
        ],
    ),
    create=extend_schema(tags=["patients"], description="Register a new patient"),
    retrieve=extend_schema(tags=["patients"], description="Get patient details"),
    update=extend_schema(tags=["patients"], description="Update patient record"),
    partial_update=extend_schema(tags=["patients"], description="Partial update patient"),
    destroy=extend_schema(tags=["patients"], description="Deactivate patient record"),
)
class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for patient management.

    Provides CRUD operations for patient records with role-based access:
    - All authenticated staff can view patients
    - Admin and clinical staff can create/update patients
    - Only admins can deactivate patients
    """

    queryset = Patient.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["gender", "blood_type", "is_active", "city", "state"]
    search_fields = ["mrn", "first_name", "last_name", "email", "phone"]
    ordering_fields = ["last_name", "first_name", "date_of_birth", "created_at"]
    ordering = ["last_name", "first_name"]

    def get_serializer_class(self):
        if self.action == "list":
            return PatientListSerializer
        if self.action == "create":
            return PatientCreateSerializer
        if self.action in ["update", "partial_update"]:
            return PatientUpdateSerializer
        return PatientDetailSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [CanViewPatients()]
        if self.action in ["create", "update", "partial_update"]:
            return [IsAdminOrClinicalStaff()]
        if self.action == "destroy":
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Filter queryset to only show active patients by default."""
        queryset = super().get_queryset()

        # Admins can see all patients, others only active
        if not self.request.user.is_admin:
            queryset = queryset.filter(is_active=True)

        return queryset

    def create(self, request, *args, **kwargs):
        """Create a patient and return full details."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = serializer.save()

        # Return full patient details using detail serializer
        detail_serializer = PatientDetailSerializer(patient)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete - deactivate patient instead of deleting.
        """
        patient = self.get_object()
        patient.is_active = False
        patient.save()

        return Response({"message": f"Patient {patient.mrn} has been deactivated."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    @extend_schema(tags=["patients"], responses={200: PatientDetailSerializer})
    def activate(self, request, pk=None):
        """Reactivate a deactivated patient."""
        patient = self.get_object()
        patient.is_active = True
        patient.save()

        return Response({"message": f"Patient {patient.mrn} has been activated."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], permission_classes=[CanViewPatients])
    @extend_schema(
        tags=["patients"],
        parameters=[
            OpenApiParameter(name="ssn", description="SSN to search for", required=True),
        ],
        responses={200: PatientDetailSerializer},
    )
    def find_by_ssn(self, request):
        """
        Find a patient by their SSN.

        This performs a secure lookup using the SSN hash.
        """
        ssn = request.query_params.get("ssn")
        if not ssn:
            return Response({"error": "SSN parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        patient = Patient.find_by_ssn(ssn)
        if not patient:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientDetailSerializer(patient)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAdmin])
    @extend_schema(tags=["patients"])
    def statistics(self, request):
        """Get patient statistics (admin only)."""
        from django.db.models import Count
        from django.db.models.functions import TruncMonth

        total = Patient.objects.count()
        active = Patient.objects.filter(is_active=True).count()

        gender_breakdown = dict(
            Patient.objects.values("gender").annotate(count=Count("id")).values_list("gender", "count")
        )

        blood_type_breakdown = dict(
            Patient.objects.values("blood_type").annotate(count=Count("id")).values_list("blood_type", "count")
        )

        return Response(
            {
                "total_patients": total,
                "active_patients": active,
                "inactive_patients": total - active,
                "by_gender": gender_breakdown,
                "by_blood_type": blood_type_breakdown,
            }
        )
