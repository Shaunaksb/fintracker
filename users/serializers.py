from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile, SystemSetting


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for standard user registration (default role: VIEWER)."""

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

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


class CreateAdminSerializer(serializers.ModelSerializer):
    """Serializer for first-time admin creation."""

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

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


class UserProfileSerializer(serializers.ModelSerializer):
    """Read serializer that includes role from the related Profile."""

    role = serializers.CharField(source="profile.role", read_only=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "role")


class AssignRoleSerializer(serializers.Serializer):
    """Serializer to validate a role assignment payload."""

    role = serializers.ChoiceField(choices=Profile.Role.choices)


class DisableAdminSerializer(serializers.Serializer):
    """Serializer to toggle the is_admin_creation_enabled flag."""

    disable = serializers.BooleanField()
