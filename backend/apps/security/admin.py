"""
Django admin configuration for security app.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from django.contrib import admin

from .models import BlockedIP, RateLimitViolation, RequestLog, SecurityEvent


@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    """Admin for blocked IPs."""

    list_display = ["ip_address", "reason", "blocked_at", "blocked_by", "expires_at", "is_active"]
    list_filter = ["is_active", "blocked_at"]
    search_fields = ["ip_address", "reason"]
    readonly_fields = ["blocked_at"]
    date_hierarchy = "blocked_at"


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    """Admin for request logs."""

    list_display = [
        "timestamp",
        "ip_address",
        "method",
        "path",
        "status_code",
        "response_time_ms",
        "user",
        "is_suspicious",
        "blocked",
    ]
    list_filter = ["method", "status_code", "is_suspicious", "blocked", "timestamp"]
    search_fields = ["ip_address", "path", "user_agent"]
    readonly_fields = [
        "timestamp",
        "ip_address",
        "method",
        "path",
        "query_string",
        "user_agent",
        "user",
        "status_code",
        "response_time_ms",
        "country",
        "city",
    ]
    date_hierarchy = "timestamp"


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    """Admin for security events."""

    list_display = ["timestamp", "event_type", "severity", "ip_address", "user", "description"]
    list_filter = ["event_type", "severity", "timestamp"]
    search_fields = ["description", "ip_address"]
    readonly_fields = ["timestamp", "event_type", "description", "ip_address", "user", "metadata", "severity"]
    date_hierarchy = "timestamp"


@admin.register(RateLimitViolation)
class RateLimitViolationAdmin(admin.ModelAdmin):
    """Admin for rate limit violations."""

    list_display = ["timestamp", "ip_address", "endpoint", "limit_type", "request_count", "user"]
    list_filter = ["endpoint", "limit_type", "timestamp"]
    search_fields = ["ip_address", "endpoint"]
    readonly_fields = ["timestamp", "ip_address", "user", "endpoint", "limit_type", "request_count"]
    date_hierarchy = "timestamp"
