from rest_framework import permissions

from .models import Profile


class IsAdmin(permissions.BasePermission):
    """Allows access only to users with the ADMIN role."""

    message = "Only ADMIN users are allowed to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            return request.user.profile.role == Profile.Role.ADMIN
        except Profile.DoesNotExist:
            return False
