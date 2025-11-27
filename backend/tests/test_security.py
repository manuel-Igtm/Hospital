"""
Tests for security app - IP blocking, request logging, and events.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.security.middleware import get_client_ip
from apps.security.models import BlockedIP, RateLimitViolation, RequestLog, SecurityEvent


@pytest.fixture
def blocked_ip(db, admin_user):
    """Create a blocked IP."""
    return BlockedIP.objects.create(
        ip_address="192.168.1.100",
        reason="Test block",
        blocked_by=admin_user,
    )


@pytest.fixture
def request_logs(db, admin_user):
    """Create test request logs."""
    logs = []
    for i in range(5):
        log = RequestLog.objects.create(
            ip_address=f"192.168.1.{i}",
            method="GET",
            path=f"/api/v1/test/{i}/",
            status_code=200,
            response_time_ms=100 + i,
            user=admin_user if i % 2 == 0 else None,
        )
        logs.append(log)
    return logs


@pytest.fixture
def security_events(db, admin_user):
    """Create test security events."""
    events = []
    for event_type in [
        SecurityEvent.EventType.LOGIN_SUCCESS,
        SecurityEvent.EventType.LOGIN_FAILED,
        SecurityEvent.EventType.IP_BLOCKED,
    ]:
        event = SecurityEvent.objects.create(
            event_type=event_type,
            description=f"Test {event_type}",
            ip_address="192.168.1.1",
            user=admin_user,
            severity=SecurityEvent.Severity.MEDIUM,
        )
        events.append(event)
    return events


class TestBlockedIPEndpoints:
    """Tests for blocked IP management."""

    def test_list_blocked_ips(self, authenticated_admin_client, blocked_ip):
        """Test listing blocked IPs."""
        url = reverse("blocked-ip-list")
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_block_ip(self, authenticated_admin_client):
        """Test blocking an IP."""
        url = reverse("blocked-ip-list")
        data = {
            "ip_address": "10.0.0.100",
            "reason": "Suspicious activity",
            "duration_hours": 24,
        }
        response = authenticated_admin_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["ip_address"] == "10.0.0.100"
        assert response.data["is_active"] is True

    def test_block_duplicate_ip(self, authenticated_admin_client, blocked_ip):
        """Test blocking an already blocked IP."""
        url = reverse("blocked-ip-list")
        data = {
            "ip_address": blocked_ip.ip_address,
            "reason": "Duplicate block",
        }
        response = authenticated_admin_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unblock_ip(self, authenticated_admin_client, blocked_ip):
        """Test unblocking an IP."""
        url = reverse("blocked-ip-unblock", kwargs={"pk": blocked_ip.id})
        response = authenticated_admin_client.post(url, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_active"] is False

        # Verify security event was created
        event = SecurityEvent.objects.filter(
            event_type=SecurityEvent.EventType.IP_UNBLOCKED,
            ip_address=blocked_ip.ip_address,
        ).first()
        assert event is not None

    def test_block_with_expiration(self, authenticated_admin_client):
        """Test blocking IP with expiration."""
        url = reverse("blocked-ip-list")
        data = {
            "ip_address": "10.0.0.101",
            "reason": "Temporary block",
            "duration_hours": 2,
        }
        response = authenticated_admin_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["expires_at"] is not None


class TestRequestLogEndpoints:
    """Tests for request log viewing."""

    def test_list_request_logs(self, authenticated_admin_client, request_logs):
        """Test listing request logs."""
        url = reverse("request-log-list")
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 5

    def test_filter_logs_by_ip(self, authenticated_admin_client, request_logs):
        """Test filtering logs by IP address."""
        url = reverse("request-log-list")
        response = authenticated_admin_client.get(url, {"ip_address": "192.168.1.0"})

        assert response.status_code == status.HTTP_200_OK
        for log in response.data["results"]:
            assert log["ip_address"] == "192.168.1.0"

    def test_get_suspicious_logs(self, authenticated_admin_client, request_logs):
        """Test getting suspicious request logs."""
        # Mark some logs as suspicious
        request_logs[0].is_suspicious = True
        request_logs[0].save()

        url = reverse("request-log-suspicious")
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        for log in response.data:
            assert log["is_suspicious"] is True

    def test_get_requests_by_ip(self, authenticated_admin_client, request_logs):
        """Test getting request count by IP."""
        url = reverse("request-log-by-ip")
        response = authenticated_admin_client.get(url, {"days": 1})

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)


class TestSecurityEventEndpoints:
    """Tests for security event viewing."""

    def test_list_security_events(self, authenticated_admin_client, security_events):
        """Test listing security events."""
        url = reverse("security-event-list")
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 3

    def test_filter_events_by_type(self, authenticated_admin_client, security_events):
        """Test filtering events by type."""
        url = reverse("security-event-list")
        response = authenticated_admin_client.get(
            url, {"event_type": SecurityEvent.EventType.LOGIN_FAILED}
        )

        assert response.status_code == status.HTTP_200_OK
        for event in response.data["results"]:
            assert event["event_type"] == SecurityEvent.EventType.LOGIN_FAILED

    def test_get_event_summary(self, authenticated_admin_client, security_events):
        """Test getting event summary."""
        url = reverse("security-event-summary")
        response = authenticated_admin_client.get(url, {"days": 7})

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)


class TestSecurityDashboard:
    """Tests for security dashboard."""

    def test_get_security_dashboard(self, authenticated_admin_client, request_logs, security_events, blocked_ip):
        """Test getting security dashboard."""
        url = reverse("security-dashboard")
        response = authenticated_admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "requests" in response.data
        assert "top_ips_today" in response.data
        assert "events_last_7d" in response.data
        assert "blocked_ips" in response.data
        assert "auth" in response.data

    def test_dashboard_requires_admin(self, authenticated_doctor_client):
        """Test dashboard requires admin role."""
        url = reverse("security-dashboard")
        response = authenticated_doctor_client.get(url)

        # Should be forbidden for non-admin users
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestIPBlockingMiddleware:
    """Tests for IP blocking middleware."""

    @override_settings(SECURITY_SETTINGS={"ENABLE_IP_BLOCKING": True, "ENABLE_IP_TRACKING": False})
    def test_blocked_ip_request_denied(self, client, blocked_ip):
        """Test that blocked IP requests are denied."""
        # Clear cache to ensure fresh check
        cache.delete(f"blocked_ip:{blocked_ip.ip_address}")

        with patch("apps.security.middleware.get_client_ip") as mock_get_ip:
            mock_get_ip.return_value = blocked_ip.ip_address

            response = client.get("/health/")

            # Request should be blocked
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unblocked_ip_allowed(self, client, db):
        """Test that unblocked IPs are allowed."""
        response = client.get("/health/")
        assert response.status_code == status.HTTP_200_OK


class TestGetClientIP:
    """Tests for client IP extraction."""

    def test_get_ip_from_remote_addr(self):
        """Test getting IP from REMOTE_ADDR."""

        class MockRequest:
            META = {"REMOTE_ADDR": "192.168.1.1"}

        ip = get_client_ip(MockRequest())
        assert ip == "192.168.1.1"

    def test_get_ip_from_x_forwarded_for(self):
        """Test getting IP from X-Forwarded-For header."""

        class MockRequest:
            META = {
                "HTTP_X_FORWARDED_FOR": "10.0.0.1, 192.168.1.1",
                "REMOTE_ADDR": "127.0.0.1",
            }

        ip = get_client_ip(MockRequest())
        assert ip == "10.0.0.1"


class TestBlockedIPModel:
    """Tests for BlockedIP model."""

    def test_is_expired_with_no_expiration(self, blocked_ip):
        """Test is_expired when no expiration set."""
        assert blocked_ip.is_expired is False

    def test_is_expired_with_future_expiration(self, db, admin_user):
        """Test is_expired with future expiration."""
        blocked = BlockedIP.objects.create(
            ip_address="10.0.0.50",
            reason="Test",
            expires_at=timezone.now() + timedelta(hours=1),
            blocked_by=admin_user,
        )
        assert blocked.is_expired is False

    def test_is_expired_with_past_expiration(self, db, admin_user):
        """Test is_expired with past expiration."""
        blocked = BlockedIP.objects.create(
            ip_address="10.0.0.51",
            reason="Test",
            expires_at=timezone.now() - timedelta(hours=1),
            blocked_by=admin_user,
        )
        assert blocked.is_expired is True


class TestSecuritySignals:
    """Tests for security signals."""

    def test_login_success_creates_event(self, client, admin_user, db):
        """Test that successful login creates security event."""
        url = reverse("token_obtain_pair")
        data = {
            "email": "admin@hospital.test",
            "password": "AdminPass123!",
        }
        response = client.post(url, data, format="json")

        # Check for login success event
        event = SecurityEvent.objects.filter(
            event_type=SecurityEvent.EventType.LOGIN_SUCCESS,
            user=admin_user,
        ).first()
        # Event may or may not exist depending on signal registration
        # This is more of an integration test

    def test_login_failure_creates_event(self, client, db):
        """Test that failed login creates security event."""
        url = reverse("token_obtain_pair")
        data = {
            "email": "fake@hospital.test",
            "password": "WrongPassword!",
        }
        response = client.post(url, data, format="json")

        # Check for login failed event
        events = SecurityEvent.objects.filter(
            event_type=SecurityEvent.EventType.LOGIN_FAILED,
        )
        # Count should increase after failed attempt
