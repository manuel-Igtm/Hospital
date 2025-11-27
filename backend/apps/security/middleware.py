"""
Security middleware for IP tracking, blocking, and request logging.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

import logging
import time
from typing import Callable

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.utils import timezone

logger = logging.getLogger(__name__)


def get_client_ip(request: HttpRequest) -> str:
    """
    Get the client's IP address from the request.

    Handles X-Forwarded-For header for proxied requests.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Take the first IP in the chain (client IP)
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "127.0.0.1")
    return ip


class IPBlockingMiddleware:
    """
    Middleware to block requests from blacklisted IP addresses.

    Checks BlockedIP model and caches results for performance.
    """

    CACHE_PREFIX = "blocked_ip:"
    CACHE_TTL = 300  # 5 minutes

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Check if IP blocking is enabled
        security_settings = getattr(settings, "SECURITY_SETTINGS", {})
        if not security_settings.get("ENABLE_IP_BLOCKING", True):
            return self.get_response(request)

        ip = get_client_ip(request)

        if self._is_ip_blocked(ip):
            logger.warning(f"Blocked request from blacklisted IP: {ip}")
            self._log_blocked_request(request, ip)
            return HttpResponseForbidden("Access denied")

        return self.get_response(request)

    def _is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked, using cache for performance."""
        cache_key = f"{self.CACHE_PREFIX}{ip}"

        # Check cache first
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        # Check database
        from apps.security.models import BlockedIP

        blocked = BlockedIP.objects.filter(
            ip_address=ip,
            is_active=True,
        ).exists()

        # Check if any non-expired blocks exist
        if blocked:
            block = BlockedIP.objects.filter(
                ip_address=ip,
                is_active=True,
            ).first()
            if block and block.is_expired:
                blocked = False

        # Cache the result
        cache.set(cache_key, blocked, self.CACHE_TTL)

        return blocked

    def _log_blocked_request(self, request: HttpRequest, ip: str):
        """Log blocked request to database."""
        from apps.security.models import RequestLog

        RequestLog.objects.create(
            ip_address=ip,
            method=request.method,
            path=request.path,
            query_string=request.META.get("QUERY_STRING", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            user=request.user if request.user.is_authenticated else None,
            blocked=True,
        )


class RequestLoggingMiddleware:
    """
    Middleware to log all requests for security auditing.

    Logs request details including IP, path, user, and response time.
    """

    # Paths to exclude from logging (health checks, static, etc.)
    EXCLUDE_PATHS = [
        "/health/",
        "/ping/",
        "/static/",
        "/media/",
        "/__debug__/",
    ]

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Check if request logging is enabled
        security_settings = getattr(settings, "SECURITY_SETTINGS", {})
        if not security_settings.get("ENABLE_IP_TRACKING", True):
            return self.get_response(request)

        # Skip excluded paths
        if any(request.path.startswith(path) for path in self.EXCLUDE_PATHS):
            return self.get_response(request)

        # Record start time
        start_time = time.time()

        # Get client IP
        ip = get_client_ip(request)

        # Process request
        response = self.get_response(request)

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)

        # Log request asynchronously (or directly if Celery not available)
        self._log_request(request, response, ip, response_time_ms)

        return response

    def _log_request(
        self,
        request: HttpRequest,
        response: HttpResponse,
        ip: str,
        response_time_ms: int,
    ):
        """Log request to database."""
        # Only log if security logging is enabled
        if not getattr(settings, "SECURITY_LOG_REQUESTS", True):
            return

        try:
            from apps.security.models import RequestLog

            RequestLog.objects.create(
                ip_address=ip,
                method=request.method,
                path=request.path[:500],  # Truncate to field max length
                query_string=request.META.get("QUERY_STRING", "")[:1000],
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                user=request.user if request.user.is_authenticated else None,
                status_code=response.status_code,
                response_time_ms=response_time_ms,
            )
        except Exception as e:
            # Don't let logging failures break the request
            logger.error(f"Failed to log request: {e}")


class RateLimitMiddleware:
    """
    Custom rate limiting middleware.

    Provides more granular rate limiting than DRF's built-in throttling.
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        ip = get_client_ip(request)

        # Check rate limits for sensitive endpoints
        if self._is_rate_limited(request, ip):
            logger.warning(f"Rate limited request from {ip} to {request.path}")
            self._log_rate_limit_violation(request, ip)
            return HttpResponse(
                '{"error": "Too many requests. Please try again later."}',
                content_type="application/json",
                status=429,
            )

        return self.get_response(request)

    def _is_rate_limited(self, request: HttpRequest, ip: str) -> bool:
        """Check if request should be rate limited."""
        # Define rate limits for sensitive endpoints
        rate_limits = {
            "/api/v1/auth/login/": {"limit": 5, "window": 60},  # 5 per minute
            "/api/v1/auth/register/": {"limit": 3, "window": 60},  # 3 per minute
            "/api/v1/billing/mpesa/stk-push/": {"limit": 10, "window": 60},  # 10 per minute
        }

        path = request.path
        if path not in rate_limits:
            return False

        config = rate_limits[path]
        cache_key = f"rate_limit:{ip}:{path}"

        # Get current count
        current = cache.get(cache_key, 0)

        if current >= config["limit"]:
            return True

        # Increment counter
        cache.set(cache_key, current + 1, config["window"])

        return False

    def _log_rate_limit_violation(self, request: HttpRequest, ip: str):
        """Log rate limit violation."""
        try:
            from apps.security.models import RateLimitViolation

            RateLimitViolation.objects.create(
                ip_address=ip,
                user=request.user if request.user.is_authenticated else None,
                endpoint=request.path,
                limit_type="endpoint",
                request_count=0,  # Could calculate actual count
            )
        except Exception as e:
            logger.error(f"Failed to log rate limit violation: {e}")


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to responses.
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        # Add security headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Add CSP header for API responses
        if request.path.startswith("/api/"):
            response["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"

        return response
