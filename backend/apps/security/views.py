"""
Security views for managing blocked IPs and viewing logs.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from datetime import timedelta

from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import UserRole

from .models import BlockedIP, RateLimitViolation, RequestLog, SecurityEvent
from .serializers import (
    BlockedIPSerializer,
    BlockIPSerializer,
    RateLimitViolationSerializer,
    RequestLogSerializer,
    SecurityEventSerializer,
)


class IsAdminUser(BasePermission):
    """Permission class to check if user is admin."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.ADMIN

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role == UserRole.ADMIN


class BlockedIPViewSet(viewsets.ModelViewSet):
    """ViewSet for managing blocked IPs."""

    queryset = BlockedIP.objects.all()
    serializer_class = BlockedIPSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ["is_active"]
    search_fields = ["ip_address", "reason"]
    ordering_fields = ["blocked_at"]
    ordering = ["blocked_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return BlockIPSerializer
        return BlockedIPSerializer

    def create(self, request, *args, **kwargs):
        """Block an IP and return full serialized response."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(blocked_by=request.user)

        # Clear cache for this IP
        cache_key = f"blocked_ip:{instance.ip_address}"
        cache.delete(cache_key)

        # Log security event
        SecurityEvent.objects.create(
            event_type=SecurityEvent.EventType.IP_BLOCKED,
            description=f"IP {instance.ip_address} blocked: {instance.reason}",
            ip_address=instance.ip_address,
            user=request.user,
            severity=SecurityEvent.Severity.MEDIUM,
        )

        # Return full BlockedIPSerializer response
        response_serializer = BlockedIPSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def unblock(self, request, pk=None):
        """Unblock an IP address."""
        blocked_ip = self.get_object()
        blocked_ip.is_active = False
        blocked_ip.save()

        # Clear cache
        cache_key = f"blocked_ip:{blocked_ip.ip_address}"
        cache.delete(cache_key)

        # Log security event
        SecurityEvent.objects.create(
            event_type=SecurityEvent.EventType.IP_UNBLOCKED,
            description=f"IP {blocked_ip.ip_address} unblocked",
            ip_address=blocked_ip.ip_address,
            user=request.user,
            severity=SecurityEvent.Severity.LOW,
        )

        return Response(BlockedIPSerializer(blocked_ip).data)


class RequestLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing request logs (read-only)."""

    queryset = RequestLog.objects.select_related("user")
    serializer_class = RequestLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ["ip_address", "method", "status_code", "is_suspicious", "blocked"]
    search_fields = ["ip_address", "path", "user_agent"]
    ordering_fields = ["timestamp", "response_time_ms"]
    ordering = ["timestamp"]

    def get_queryset(self):
        """Filter by date range if provided."""
        queryset = super().get_queryset()

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)

        return queryset

    @action(detail=False, methods=["get"])
    def suspicious(self, request):
        """Get suspicious requests."""
        logs = self.get_queryset().filter(is_suspicious=True)[:100]
        return Response(RequestLogSerializer(logs, many=True).data)

    @action(detail=False, methods=["get"])
    def by_ip(self, request):
        """Get request count by IP."""
        days = int(request.query_params.get("days", 1))
        start_date = timezone.now() - timedelta(days=days)

        ip_stats = (
            RequestLog.objects.filter(timestamp__gte=start_date)
            .values("ip_address")
            .annotate(count=Count("id"))
            .order_by("-count")[:50]
        )

        return Response(list(ip_stats))


class SecurityEventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing security events (read-only)."""

    queryset = SecurityEvent.objects.select_related("user")
    serializer_class = SecurityEventSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ["event_type", "severity"]
    search_fields = ["description", "ip_address"]
    ordering_fields = ["timestamp", "severity"]
    ordering = ["-timestamp"]

    def get_queryset(self):
        """Filter by date range if provided."""
        queryset = super().get_queryset()

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)

        return queryset

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get event summary by type."""
        days = int(request.query_params.get("days", 7))
        start_date = timezone.now() - timedelta(days=days)

        summary = (
            SecurityEvent.objects.filter(timestamp__gte=start_date)
            .values("event_type", "severity")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return Response(list(summary))


class RateLimitViolationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing rate limit violations (read-only)."""

    queryset = RateLimitViolation.objects.select_related("user")
    serializer_class = RateLimitViolationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ["ip_address", "endpoint"]
    ordering_fields = ["timestamp"]
    ordering = ["-timestamp"]


class SecurityDashboardView(APIView):
    """
    Security dashboard with summary statistics.

    GET /api/v1/security/dashboard/
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        """Return security dashboard data."""
        now = timezone.now()
        today = now.date()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        # Request statistics
        requests_24h = RequestLog.objects.filter(timestamp__gte=last_24h).count()
        blocked_24h = RequestLog.objects.filter(
            timestamp__gte=last_24h, blocked=True
        ).count()
        suspicious_24h = RequestLog.objects.filter(
            timestamp__gte=last_24h, is_suspicious=True
        ).count()

        # Top IPs today
        top_ips = (
            RequestLog.objects.filter(timestamp__date=today)
            .values("ip_address")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        # Security events summary
        events_7d = (
            SecurityEvent.objects.filter(timestamp__gte=last_7d)
            .values("event_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Active blocks
        active_blocks = BlockedIP.objects.filter(is_active=True).count()

        # Rate limit violations
        rate_limit_24h = RateLimitViolation.objects.filter(
            timestamp__gte=last_24h
        ).count()

        # Failed logins
        failed_logins_24h = SecurityEvent.objects.filter(
            timestamp__gte=last_24h,
            event_type=SecurityEvent.EventType.LOGIN_FAILED,
        ).count()

        return Response(
            {
                "requests": {
                    "last_24h": requests_24h,
                    "blocked_24h": blocked_24h,
                    "suspicious_24h": suspicious_24h,
                },
                "top_ips_today": list(top_ips),
                "events_last_7d": list(events_7d),
                "blocked_ips": {
                    "active": active_blocks,
                },
                "rate_limits": {
                    "violations_24h": rate_limit_24h,
                },
                "auth": {
                    "failed_logins_24h": failed_logins_24h,
                },
                "generated_at": now.isoformat(),
            }
        )
