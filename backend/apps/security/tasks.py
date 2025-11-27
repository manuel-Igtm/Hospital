"""
Celery tasks for security operations.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="apps.security.tasks.cleanup_old_request_logs")
def cleanup_old_request_logs():
    """
    Delete old request logs based on retention policy.

    Runs daily via Celery Beat.
    """
    from apps.security.models import RequestLog

    retention_days = getattr(settings, "SECURITY_REQUEST_LOG_RETENTION_DAYS", 90)
    cutoff_date = timezone.now() - timedelta(days=retention_days)

    deleted_count, _ = RequestLog.objects.filter(timestamp__lt=cutoff_date).delete()

    logger.info(f"Cleaned up {deleted_count} old request logs (older than {retention_days} days)")

    return {"deleted": deleted_count, "retention_days": retention_days}


@shared_task(name="apps.security.tasks.cleanup_expired_blocks")
def cleanup_expired_blocks():
    """
    Deactivate expired IP blocks.

    Runs hourly via Celery Beat.
    """
    from django.core.cache import cache

    from apps.security.models import BlockedIP

    now = timezone.now()
    expired = BlockedIP.objects.filter(
        is_active=True,
        expires_at__isnull=False,
        expires_at__lt=now,
    )

    updated_count = 0
    for block in expired:
        block.is_active = False
        block.save(update_fields=["is_active"])

        # Clear cache for this IP
        cache.delete(f"blocked_ip:{block.ip_address}")
        updated_count += 1

        logger.info(f"Deactivated expired block for IP: {block.ip_address}")

    return {"deactivated": updated_count}


@shared_task(name="apps.security.tasks.detect_suspicious_activity")
def detect_suspicious_activity():
    """
    Analyze request logs for suspicious patterns.

    Runs every 15 minutes via Celery Beat.
    """
    from django.db.models import Count

    from apps.security.models import BlockedIP, RequestLog, SecurityEvent

    now = timezone.now()
    window = now - timedelta(minutes=15)

    # Detect IPs with high request volumes
    suspicious_ips = (
        RequestLog.objects.filter(
            timestamp__gte=window,
            blocked=False,
        )
        .values("ip_address")
        .annotate(count=Count("id"))
        .filter(count__gte=500)  # More than 500 requests in 15 min
    )

    flagged = 0
    for item in suspicious_ips:
        ip = item["ip_address"]

        # Flag requests as suspicious
        RequestLog.objects.filter(
            ip_address=ip,
            timestamp__gte=window,
            is_suspicious=False,
        ).update(is_suspicious=True)

        # Log security event
        SecurityEvent.objects.create(
            event_type=SecurityEvent.EventType.SUSPICIOUS_ACTIVITY,
            description=f"High request volume detected from {ip}: {item['count']} requests in 15 minutes",
            ip_address=ip,
            severity=SecurityEvent.Severity.HIGH,
            metadata={"request_count": item["count"]},
        )

        flagged += 1
        logger.warning(f"Suspicious activity detected from {ip}: {item['count']} requests")

    # Detect IPs with many failed requests (4xx/5xx)
    error_ips = (
        RequestLog.objects.filter(
            timestamp__gte=window,
            status_code__gte=400,
        )
        .values("ip_address")
        .annotate(count=Count("id"))
        .filter(count__gte=50)  # More than 50 errors in 15 min
    )

    for item in error_ips:
        ip = item["ip_address"]

        # Check if already blocked
        if BlockedIP.objects.filter(ip_address=ip, is_active=True).exists():
            continue

        # Log security event
        SecurityEvent.objects.create(
            event_type=SecurityEvent.EventType.SUSPICIOUS_ACTIVITY,
            description=f"High error rate from {ip}: {item['count']} failed requests in 15 minutes",
            ip_address=ip,
            severity=SecurityEvent.Severity.MEDIUM,
            metadata={"error_count": item["count"]},
        )

        flagged += 1

    return {"flagged_ips": flagged}


@shared_task(name="apps.security.tasks.generate_security_report")
def generate_security_report():
    """
    Generate daily security summary report.

    Runs daily via Celery Beat.
    """
    from django.db.models import Count

    from apps.security.models import BlockedIP, RateLimitViolation, RequestLog, SecurityEvent

    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # Gather statistics
    total_requests = RequestLog.objects.filter(timestamp__date=yesterday).count()
    blocked_requests = RequestLog.objects.filter(timestamp__date=yesterday, blocked=True).count()
    suspicious_requests = RequestLog.objects.filter(timestamp__date=yesterday, is_suspicious=True).count()

    security_events = (
        SecurityEvent.objects.filter(timestamp__date=yesterday).values("event_type").annotate(count=Count("id"))
    )

    rate_limit_violations = RateLimitViolation.objects.filter(timestamp__date=yesterday).count()

    new_blocks = BlockedIP.objects.filter(blocked_at__date=yesterday).count()

    report = {
        "date": str(yesterday),
        "total_requests": total_requests,
        "blocked_requests": blocked_requests,
        "suspicious_requests": suspicious_requests,
        "rate_limit_violations": rate_limit_violations,
        "new_ip_blocks": new_blocks,
        "security_events": {item["event_type"]: item["count"] for item in security_events},
    }

    logger.info(f"Security report for {yesterday}: {report}")

    return report
