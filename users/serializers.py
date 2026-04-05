import re

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile, SystemSetting


# ─── Shared helpers ──────────────────────────────────────────────────────────

def _normalize_name(value: str) -> str:
    """Strip surrounding whitespace and collapse internal spaces."""
    return " ".join(value.split())


def _validate_name(value: str, field: str) -> str:
    value = _normalize_name(value)
    if not value:
        raise serializers.ValidationError(f"{field} cannot be blank or whitespace.")
    if len(value) > 150:
        raise serializers.ValidationError(f"{field} must be 150 characters or fewer.")
    if not re.match(r"^[A-Za-z\s\-']+$", value):
        raise serializers.ValidationError(
            f"{field} can only contain letters, spaces, hyphens, and apostrophes."
        )
    return value


def _validate_password_strength(value: str) -> str:
    if len(value) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters.")
    if not re.search(r"[A-Z]", value):
        raise serializers.ValidationError(
            "Password must contain at least one uppercase letter."
        )
    if not re.search(r"[a-z]", value):
        raise serializers.ValidationError(
            "Password must contain at least one lowercase letter."
        )
    if not re.search(r"\d", value):
        raise serializers.ValidationError(
            "Password must contain at least one digit."
        )
    return value


# ─── Base registration serializer ────────────────────────────────────────────

class _BaseUserSerializer(serializers.Serializer):
    """Shared fields and validators for registration-style serializers."""

    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=254)
    password = serializers.CharField(write_only=True)

    def validate_first_name(self, value):
        return _validate_name(value, "First name")

    def validate_last_name(self, value):
        return _validate_name(value, "Last name")

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        return _validate_password_strength(value)


# ─── Register ────────────────────────────────────────────────────────────────

class RegisterSerializer(_BaseUserSerializer):
    """Serializer for standard user registration (default role: VIEWER)."""

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        Profile.objects.create(user=user, role=Profile.Role.VIEWER)
        return user


# ─── Create Admin ─────────────────────────────────────────────────────────────

class CreateAdminSerializer(_BaseUserSerializer):
    """Serializer for first-time admin creation."""

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            is_staff=True,
        )
        Profile.objects.create(user=user, role=Profile.Role.ADMIN)

        # Disable further admin creation immediately after first admin is created
        setting = SystemSetting.load()
        setting.is_admin_creation_enabled = False
        setting.save()

        return user


# ─── Read ─────────────────────────────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    """Read serializer that includes role from the related Profile."""

    role = serializers.CharField(source="profile.role", read_only=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "role")


# ─── Assign role ──────────────────────────────────────────────────────────────

class AssignRoleSerializer(serializers.Serializer):
    """Serializer to validate a role assignment payload."""

    role = serializers.ChoiceField(choices=Profile.Role.choices)

    def validate_role(self, value):
        if value not in Profile.Role.values:
            raise serializers.ValidationError(
                f"Invalid role. Valid choices are: {', '.join(Profile.Role.values)}."
            )
        return value


# ─── Toggle admin creation ────────────────────────────────────────────────────

class DisableAdminSerializer(serializers.Serializer):
    """Serializer to toggle the is_admin_creation_enabled flag."""

    disable = serializers.BooleanField(
        help_text="Pass true to disable admin creation, false to re-enable it."
    )

    def validate_disable(self, value):
        if not isinstance(value, bool):
            raise serializers.ValidationError("'disable' must be a boolean (true or false).")
        return value
