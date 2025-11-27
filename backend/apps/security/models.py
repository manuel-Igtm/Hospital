"""
Security models for request logging and IP blocking.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class RequestLog(models.Model):
    """
    Log of HTTP requests for security auditing.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    # Request details
    ip_address = models.GenericIPAddressField(db_index=True, help_text="Client IP address")
    method = models.CharField(max_length=10, help_text="HTTP method")
    path = models.CharField(max_length=500, help_text="Request path")
    query_string = models.TextField(blank=True, help_text="Query string")
    user_agent = models.TextField(blank=True, help_text="User agent")

    # User info (if authenticated)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="request_logs",
        help_text="Authenticated user",
    )

    # Response details
    status_code = models.IntegerField(null=True, blank=True, help_text="HTTP status code")
    response_time_ms = models.IntegerField(null=True, blank=True, help_text="Response time in ms")

    # Geolocation (if available)
    country = models.CharField(max_length=100, blank=True, help_text="Country from GeoIP")
    city = models.CharField(max_length=100, blank=True, help_text="City from GeoIP")

    # Flags
    is_suspicious = models.BooleanField(default=False, help_text="Flagged as suspicious")
    blocked = models.BooleanField(default=False, help_text="Request was blocked")

    class Meta:
        db_table = "security_request_logs"
        verbose_name = "Request Log"
        verbose_name_plural = "Request Logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["ip_address", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["is_suspicious"]),
        ]

    def __str__(self):
        return f"{self.method} {self.path} from {self.ip_address} at {self.timestamp}"


class BlockedIP(models.Model):
    """
    Blocked IP addresses.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField(unique=True, db_index=True, help_text="Blocked IP address")
    reason = models.TextField(blank=True, help_text="Reason for blocking")
    blocked_at = models.DateTimeField(auto_now_add=True, help_text="When the IP was blocked")
    blocked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blocked_ips",
        help_text="User who blocked this IP",
    )
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When the block expires (null = permanent)")
    is_active = models.BooleanField(default=True, help_text="Whether block is active")

    class Meta:
        db_table = "security_blocked_ips"
        verbose_name = "Blocked IP"
        verbose_name_plural = "Blocked IPs"
        ordering = ["-blocked_at"]

    def __str__(self):
        return f"{self.ip_address} (blocked at {self.blocked_at})"

    @property
    def is_expired(self):
        """Check if the block has expired."""
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at


class SecurityEvent(models.Model):
    """
    Security events for auditing.
    """

    class EventType(models.TextChoices):
        LOGIN_SUCCESS = "LOGIN_SUCCESS", "Login Success"
        LOGIN_FAILED = "LOGIN_FAILED", "Login Failed"
        LOGOUT = "LOGOUT", "Logout"
        PASSWORD_CHANGE = "PASSWORD_CHANGE", "Password Changed"
        PASSWORD_RESET = "PASSWORD_RESET", "Password Reset"
        ACCOUNT_LOCKED = "ACCOUNT_LOCKED", "Account Locked"
        IP_BLOCKED = "IP_BLOCKED", "IP Blocked"
        IP_UNBLOCKED = "IP_UNBLOCKED", "IP Unblocked"
        RATE_LIMITED = "RATE_LIMITED", "Rate Limited"
        SUSPICIOUS_ACTIVITY = "SUSPICIOUS", "Suspicious Activity"
        DATA_ACCESS = "DATA_ACCESS", "Sensitive Data Access"
        DATA_EXPORT = "DATA_EXPORT", "Data Export"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    event_type = models.CharField(max_length=20, choices=EventType.choices, db_index=True)
    description = models.TextField(help_text="Event description")

    # Source
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="Source IP")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="security_events",
    )

    # Additional data
    metadata = models.JSONField(null=True, blank=True, help_text="Additional event data")

    # Severity
    class Severity(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.LOW,
        db_index=True,
    )

    class Meta:
        db_table = "security_events"
        verbose_name = "Security Event"
        verbose_name_plural = "Security Events"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["event_type", "timestamp"]),
            models.Index(fields=["severity", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"


class RateLimitViolation(models.Model):
    """
    Track rate limit violations.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    ip_address = models.GenericIPAddressField(db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    endpoint = models.CharField(max_length=500, help_text="Rate limited endpoint")
    limit_type = models.CharField(max_length=50, help_text="Type of rate limit")
    request_count = models.IntegerField(help_text="Number of requests in window")

    class Meta:
        db_table = "security_rate_limit_violations"
        verbose_name = "Rate Limit Violation"
        verbose_name_plural = "Rate Limit Violations"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Rate limit violation from {self.ip_address} at {self.timestamp}"
