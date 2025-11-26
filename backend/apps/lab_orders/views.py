"""
Lab Order views and viewsets.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from .models import TestType, LabOrder, LabResult, OrderStatus
from .serializers import (
    TestTypeSerializer,
    LabOrderListSerializer,
    LabOrderDetailSerializer,
    LabOrderCreateSerializer,
    LabOrderStatusUpdateSerializer,
    LabResultSerializer,
    LabResultCreateSerializer,
    LabResultReviewSerializer,
)
from apps.users.permissions import (
    IsAdmin,
    IsAdminOrDoctor,
    IsLabTech,
    IsClinicalStaff,
    CanOrderLabs,
    CanViewPatients,
)


@extend_schema_view(
    list=extend_schema(tags=['lab-orders'], description='List available test types'),
    retrieve=extend_schema(tags=['lab-orders'], description='Get test type details'),
    create=extend_schema(tags=['lab-orders'], description='Create new test type (admin)'),
    update=extend_schema(tags=['lab-orders'], description='Update test type (admin)'),
    destroy=extend_schema(tags=['lab-orders'], description='Deactivate test type (admin)'),
)
class TestTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for lab test type catalog.
    
    All authenticated users can view test types.
    Only admins can create, update, or deactivate test types.
    """
    queryset = TestType.objects.filter(is_active=True)
    serializer_class = TestTypeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['code', 'name', 'loinc_code']
    ordering_fields = ['code', 'name', 'category']
    ordering = ['category', 'code']
    
    def get_queryset(self):
        queryset = TestType.objects.all()
        # Non-admins only see active test types
        if not self.request.user.is_admin:
            queryset = queryset.filter(is_active=True)
        return queryset
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete - deactivate test type."""
        test_type = self.get_object()
        test_type.is_active = False
        test_type.save()
        return Response(
            {'message': f'Test type {test_type.code} has been deactivated.'},
            status=status.HTTP_200_OK
        )


@extend_schema_view(
    list=extend_schema(
        tags=['lab-orders'],
        description='List lab orders',
        parameters=[
            OpenApiParameter(name='status', description='Filter by status'),
            OpenApiParameter(name='priority', description='Filter by priority'),
            OpenApiParameter(name='patient', description='Filter by patient ID'),
        ]
    ),
    create=extend_schema(tags=['lab-orders'], description='Create a new lab order'),
    retrieve=extend_schema(tags=['lab-orders'], description='Get lab order details'),
)
class LabOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for lab order management.
    
    - Doctors/Nurses can create orders (CanOrderLabs permission)
    - Lab techs can view and update order status
    - All clinical staff can view orders
    """
    queryset = LabOrder.objects.select_related(
        'patient', 'test_type', 'ordering_provider', 'specimen_collected_by'
    ).all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'patient', 'ordering_provider', 'test_type']
    search_fields = ['order_number', 'patient__mrn', 'patient__last_name']
    ordering_fields = ['ordered_at', 'priority', 'status']
    ordering = ['-ordered_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LabOrderListSerializer
        if self.action == 'create':
            return LabOrderCreateSerializer
        if self.action == 'update_status':
            return LabOrderStatusUpdateSerializer
        return LabOrderDetailSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [CanOrderLabs()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [CanViewPatients()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by role
        if user.is_doctor:
            # Doctors see their own orders and orders for their patients
            queryset = queryset.filter(ordering_provider=user)
        elif user.is_lab_tech:
            # Lab techs see orders that need processing
            queryset = queryset.exclude(status__in=[
                OrderStatus.CANCELLED, OrderStatus.REVIEWED
            ])
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsClinicalStaff])
    @extend_schema(
        tags=['lab-orders'],
        request=LabOrderStatusUpdateSerializer,
        responses={200: LabOrderDetailSerializer}
    )
    def update_status(self, request, pk=None):
        """Update the order status with validation."""
        order = self.get_object()
        serializer = LabOrderStatusUpdateSerializer(
            data=request.data,
            context={'order': order, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['status']
        order.transition_to(new_status, user=request.user)
        
        return Response(LabOrderDetailSerializer(order).data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsClinicalStaff])
    @extend_schema(tags=['lab-orders'], responses={200: LabOrderDetailSerializer})
    def collect_specimen(self, request, pk=None):
        """Mark specimen as collected."""
        order = self.get_object()
        
        if not order.can_transition_to(OrderStatus.COLLECTED):
            return Response(
                {'error': f'Cannot collect specimen for order in {order.status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.transition_to(OrderStatus.COLLECTED, user=request.user)
        return Response(LabOrderDetailSerializer(order).data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrDoctor])
    @extend_schema(tags=['lab-orders'], responses={200: LabOrderDetailSerializer})
    def cancel(self, request, pk=None):
        """Cancel a lab order."""
        order = self.get_object()
        
        if not order.can_transition_to(OrderStatus.CANCELLED):
            return Response(
                {'error': f'Cannot cancel order in {order.status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.transition_to(OrderStatus.CANCELLED)
        return Response(LabOrderDetailSerializer(order).data)
    
    @action(detail=False, methods=['get'], permission_classes=[CanViewPatients])
    @extend_schema(tags=['lab-orders'])
    def my_orders(self, request):
        """Get orders created by the current user (for doctors)."""
        orders = LabOrder.objects.filter(ordering_provider=request.user)
        serializer = LabOrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsLabTech])
    @extend_schema(tags=['lab-orders'])
    def pending_results(self, request):
        """Get orders awaiting results (for lab techs)."""
        orders = LabOrder.objects.filter(
            status__in=[OrderStatus.COLLECTED, OrderStatus.IN_PROGRESS]
        ).select_related('patient', 'test_type', 'ordering_provider')
        serializer = LabOrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdmin])
    @extend_schema(tags=['lab-orders'])
    def statistics(self, request):
        """Get lab order statistics (admin only)."""
        from django.db.models import Count
        from django.db.models.functions import TruncDate
        from datetime import timedelta
        from django.utils import timezone
        
        total = LabOrder.objects.count()
        
        status_breakdown = dict(
            LabOrder.objects.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )
        
        priority_breakdown = dict(
            LabOrder.objects.values('priority')
            .annotate(count=Count('id'))
            .values_list('priority', 'count')
        )
        
        # Orders in last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        recent_orders = LabOrder.objects.filter(ordered_at__gte=week_ago).count()
        
        return Response({
            'total_orders': total,
            'recent_orders_7d': recent_orders,
            'by_status': status_breakdown,
            'by_priority': priority_breakdown,
        })


@extend_schema_view(
    list=extend_schema(tags=['lab-orders'], description='List lab results'),
    create=extend_schema(tags=['lab-orders'], description='Enter lab results'),
    retrieve=extend_schema(tags=['lab-orders'], description='Get result details'),
)
class LabResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for lab results.
    
    - Lab techs can create results
    - Doctors can review results
    - Clinical staff can view results
    """
    queryset = LabResult.objects.select_related(
        'order', 'order__patient', 'order__test_type',
        'resulted_by', 'reviewed_by'
    ).all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_abnormal', 'is_critical', 'order__patient']
    ordering_fields = ['resulted_at', 'reviewed_at']
    ordering = ['-resulted_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LabResultCreateSerializer
        if self.action == 'review':
            return LabResultReviewSerializer
        return LabResultSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsLabTech()]
        if self.action == 'review':
            return [IsAdminOrDoctor()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsClinicalStaff()]
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrDoctor])
    @extend_schema(
        tags=['lab-orders'],
        request=LabResultReviewSerializer,
        responses={200: LabResultSerializer}
    )
    def review(self, request, pk=None):
        """Review and approve lab results."""
        result = self.get_object()
        
        if result.reviewed_by:
            return Response(
                {'error': 'Results have already been reviewed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = LabResultReviewSerializer(
            result,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(LabResultSerializer(result).data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrDoctor])
    @extend_schema(tags=['lab-orders'])
    def pending_review(self, request):
        """Get results awaiting review (for doctors)."""
        results = LabResult.objects.filter(
            reviewed_by__isnull=True
        ).select_related('order', 'order__patient', 'order__test_type')
        
        # Doctors only see results for their orders
        if request.user.is_doctor:
            results = results.filter(order__ordering_provider=request.user)
        
        serializer = LabResultSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsClinicalStaff])
    @extend_schema(tags=['lab-orders'])
    def critical(self, request):
        """Get critical results that need attention."""
        results = LabResult.objects.filter(
            is_critical=True,
            reviewed_by__isnull=True
        ).select_related('order', 'order__patient', 'order__test_type')
        serializer = LabResultSerializer(results, many=True)
        return Response(serializer.data)
