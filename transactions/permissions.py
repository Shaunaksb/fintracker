from rest_framework import permissions

from users.models import Profile

WRITE_METHODS = ("POST", "PUT", "PATCH", "DELETE")
READ_ALLOWED_ROLES = (Profile.Role.ADMIN, Profile.Role.ANALYST)


class IsAdminForWrite(permissions.BasePermission):
    """
    - WRITE (POST/PUT/PATCH/DELETE): ADMIN only.
    - READ  (GET/HEAD/OPTIONS):      ADMIN and ANALYST.
    """

    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            role = request.user.profile.role
        except Profile.DoesNotExist:
            return False

        if request.method in WRITE_METHODS:
            return role == Profile.Role.ADMIN

        # Safe methods (GET, HEAD, OPTIONS)
        return role in READ_ALLOWED_ROLES
