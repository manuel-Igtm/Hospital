"""
User views and viewsets.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User, UserRole
from .permissions import IsAdmin, IsOwnerOrAdmin
from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    UserCreateSerializer,
    UserRoleUpdateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


@extend_schema(tags=["auth"])
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Login endpoint - obtain JWT access and refresh tokens.

    Returns access token (15 min), refresh token (7 days), and user info.
    """

    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(tags=["auth"])
class CustomTokenRefreshView(TokenRefreshView):
    """
    Refresh endpoint - obtain new access token using refresh token.
    """

    pass


@extend_schema(tags=["auth"])
class LogoutView(generics.GenericAPIView):
    """
    Logout endpoint - blacklist the refresh token.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={"application/json": {"type": "object", "properties": {"refresh": {"type": "string"}}}},
        responses={205: None},
    )
    def post(self, request):
        """Blacklist the provided refresh token."""
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["auth"])
class MeView(generics.RetrieveUpdateAPIView):
    """
    Current user profile endpoint.

    GET: Retrieve current user's profile.
    PATCH/PUT: Update current user's profile.
    """

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


@extend_schema(tags=["auth"])
class ChangePasswordView(generics.GenericAPIView):
    """
    Change password endpoint for authenticated users.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        """Change the current user's password."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        # Verify old password
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": ["Current password is incorrect."]}, status=status.HTTP_400_BAD_REQUEST)

        # Set new password
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"message": "Password changed successfully."})


@extend_schema_view(
    list=extend_schema(tags=["users"], description="List all users (admin only)"),
    create=extend_schema(tags=["users"], description="Create a new user (admin only)"),
    retrieve=extend_schema(tags=["users"], description="Retrieve a user"),
    update=extend_schema(tags=["users"], description="Update a user (admin only)"),
    partial_update=extend_schema(tags=["users"], description="Partial update a user"),
    destroy=extend_schema(tags=["users"], description="Deactivate a user (admin only)"),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management.

    Admins can list, create, update, and deactivate users.
    Users can view and update their own profile.
    """

    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["role", "is_active", "department"]
    search_fields = ["email", "first_name", "last_name", "license_number"]
    ordering_fields = ["date_joined", "last_name", "email"]
    ordering = ["-date_joined"]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ["update", "partial_update"]:
            # Admin can update role, others can only update profile
            if self.request.user.is_admin:
                return UserRoleUpdateSerializer
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ["list", "create", "destroy"]:
            return [IsAdmin()]
        if self.action in ["retrieve", "update", "partial_update"]:
            return [IsOwnerOrAdmin()]
        return [IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete - deactivate user instead of deleting.
        """
        user = self.get_object()

        # Prevent self-deactivation
        if user == request.user:
            return Response({"error": "You cannot deactivate your own account."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = False
        user.save()

        return Response({"message": f"User {user.email} has been deactivated."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    @extend_schema(tags=["users"], responses={200: UserSerializer})
    def activate(self, request, pk=None):
        """Reactivate a deactivated user."""
        user = self.get_object()
        user.is_active = True
        user.save()

        return Response({"message": f"User {user.email} has been activated."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], permission_classes=[IsAdmin])
    @extend_schema(tags=["users"])
    def by_role(self, request):
        """Get users grouped by role."""
        result = {}
        for role in UserRole.choices:
            users = User.objects.filter(role=role[0], is_active=True)
            result[role[0]] = UserSerializer(users, many=True).data

        return Response(result)
