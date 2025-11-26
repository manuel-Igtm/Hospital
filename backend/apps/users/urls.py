"""
URL configuration for users app.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    ChangePasswordView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    MeView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    # Auth endpoints
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="change_password"),
    # User management endpoints
    path("", include(router.urls)),
]
