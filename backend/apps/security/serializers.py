"""
Security serializers.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import BlockedIP, RateLimitViolation, RequestLog, SecurityEvent


class BlockedIPSerializer(serializers.ModelSerializer):
    """Serializer for blocked IPs."""

    blocked_by_name = serializers.CharField(source="blocked_by.get_full_name", read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = BlockedIP
        fields = [
            "id",
            "ip_address",
            "reason",
            "blocked_at",
            "blocked_by",
            "blocked_by_name",
            "expires_at",
            "is_active",
            "is_expired",
        ]
        read_only_fields = ["id", "blocked_at", "blocked_by"]


class BlockIPSerializer(serializers.Serializer):
    """Serializer for blocking an IP."""

    ip_address = serializers.IPAddressField()
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)
    duration_hours = serializers.IntegerField(required=False, min_value=1, max_value=8760)  # Max 1 year

    def validate_ip_address(self, value):
        """Check if IP is already blocked."""
        if BlockedIP.objects.filter(ip_address=value, is_active=True).exists():
            raise serializers.ValidationError("IP is already blocked")
        return value

    def create(self, validated_data):
        """Create blocked IP record."""
        duration = validated_data.pop("duration_hours", None)
        expires_at = None
        if duration:
            expires_at = timezone.now() + timedelta(hours=duration)

        return BlockedIP.objects.create(
            ip_address=validated_data["ip_address"],
            reason=validated_data.get("reason", ""),
            expires_at=expires_at,
            blocked_by=validated_data.get("blocked_by"),
        )


class RequestLogSerializer(serializers.ModelSerializer):
    """Serializer for request logs."""

    username = serializers.CharField(source="user.username", read_only=True, allow_null=True)

    class Meta:
        model = RequestLog
        fields = [
            "id",
            "timestamp",
            "ip_address",
            "method",
            "path",
            "query_string",
            "user_agent",
            "user",
            "username",
            "status_code",
            "response_time_ms",
            "country",
            "city",
            "is_suspicious",
            "blocked",
        ]


class SecurityEventSerializer(serializers.ModelSerializer):
    """Serializer for security events."""

    username = serializers.CharField(source="user.username", read_only=True, allow_null=True)
    event_type_display = serializers.CharField(source="get_event_type_display", read_only=True)
    severity_display = serializers.CharField(source="get_severity_display", read_only=True)

    class Meta:
        model = SecurityEvent
        fields = [
            "id",
            "timestamp",
            "event_type",
            "event_type_display",
            "description",
            "ip_address",
            "user",
            "username",
            "metadata",
            "severity",
            "severity_display",
        ]


class RateLimitViolationSerializer(serializers.ModelSerializer):
    """Serializer for rate limit violations."""

    username = serializers.CharField(source="user.username", read_only=True, allow_null=True)

    class Meta:
        model = RateLimitViolation
        fields = [
            "id",
            "timestamp",
            "ip_address",
            "user",
            "username",
            "endpoint",
            "limit_type",
            "request_count",
        ]
