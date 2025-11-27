"""
Security signals for logging authentication events.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .models import SecurityEvent

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP from request."""
    if request is None:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@receiver(user_logged_in)
def log_login_success(sender, request, user, **kwargs):
    """Log successful login."""
    ip = get_client_ip(request)
    logger.info(f"User {user.username} logged in from {ip}")

    SecurityEvent.objects.create(
        event_type=SecurityEvent.EventType.LOGIN_SUCCESS,
        description=f"User {user.username} logged in successfully",
        ip_address=ip,
        user=user,
        severity=SecurityEvent.Severity.LOW,
    )


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    """Log logout."""
    if user is None:
        return

    ip = get_client_ip(request)
    logger.info(f"User {user.username} logged out from {ip}")

    SecurityEvent.objects.create(
        event_type=SecurityEvent.EventType.LOGOUT,
        description=f"User {user.username} logged out",
        ip_address=ip,
        user=user,
        severity=SecurityEvent.Severity.LOW,
    )


@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    """Log failed login attempt."""
    ip = get_client_ip(request)
    username = credentials.get("username", "unknown")
    logger.warning(f"Failed login attempt for {username} from {ip}")

    SecurityEvent.objects.create(
        event_type=SecurityEvent.EventType.LOGIN_FAILED,
        description=f"Failed login attempt for username: {username}",
        ip_address=ip,
        severity=SecurityEvent.Severity.MEDIUM,
        metadata={"username": username},
    )
