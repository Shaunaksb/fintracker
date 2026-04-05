from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile, SystemSetting
from .permissions import IsAdmin
from .serializers import (
    AssignRoleSerializer,
    CreateAdminSerializer,
    DisableAdminSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    POST /api/users/register/
    Public endpoint. Creates a user with the default VIEWER role.
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserProfileSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class CreateAdminView(generics.CreateAPIView):
    """
    POST /api/users/create-admin/
    Public endpoint. Creates the first (and only) admin user.

    Rules:
    - Returns 403 if an ADMIN profile already exists.
    - Returns 403 if SystemSetting.is_admin_creation_enabled is False.
    - On success, immediately sets is_admin_creation_enabled = False.
    """

    serializer_class = CreateAdminSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # Guard: check if admin creation is permitted
        setting = SystemSetting.load()
        admin_exists = Profile.objects.filter(role=Profile.Role.ADMIN).exists()

        if admin_exists or not setting.is_admin_creation_enabled:
            return Response(
                {"detail": "Admin creation is disabled or an admin already exists."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # Flag is toggled inside serializer.create()
        return Response(
            UserProfileSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class DisableAdminView(APIView):
    """
    POST /api/users/admin/toggle-creation/
    ADMIN only. Accepts {"disable": true/false} to toggle is_admin_creation_enabled.
    Note: 'disable: true' → is_admin_creation_enabled = False (i.e. creation is OFF).
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, *args, **kwargs):
        serializer = DisableAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        disable = serializer.validated_data["disable"]
        setting = SystemSetting.load()
        # If disable=True, creation is disabled (False); if disable=False, creation is enabled (True)
        setting.is_admin_creation_enabled = not disable
        setting.save()

        return Response(
            {
                "detail": "Setting updated.",
                "is_admin_creation_enabled": setting.is_admin_creation_enabled,
            },
            status=status.HTTP_200_OK,
        )


class AssignRoleView(APIView):
    """
    PATCH /api/users/<user_id>/assign-role/
    ADMIN only. Updates the role of a target user.
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, user_id, *args, **kwargs):
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Prevent an admin from accidentally removing their own admin role
        if target_user == request.user:
            return Response(
                {"detail": "You cannot change your own role."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile, _ = Profile.objects.get_or_create(user=target_user)
        profile.role = serializer.validated_data["role"]
        profile.save()

        return Response(
            {
                "detail": "Role updated successfully.",
                "user": UserProfileSerializer(target_user).data,
            },
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """
    GET /api/users/me/
    Returns the current authenticated user's profile and role.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(UserProfileSerializer(request.user).data)
