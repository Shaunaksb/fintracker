from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Profile, SystemSetting


class UserAuthTests(APITestCase):
    def setUp(self):
        # Clear SystemSetting to ensure a fresh state
        SystemSetting.objects.all().delete()
        self.register_url = reverse("users:register")
        self.create_admin_url = reverse("users:create-admin")
        self.me_url = reverse("users:me")

    def test_registration_viewer_default(self):
        """Test that a new registered user gets the VIEWER role by default."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password": "Password123!",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], Profile.Role.VIEWER)

        user = User.objects.get(email="john@example.com")
        self.assertEqual(user.profile.role, Profile.Role.VIEWER)

    def test_first_admin_creation_flow(self):
        """Test the singleton-like logic for creating the first admin."""
        data = {
            "first_name": "Admin",
            "last_name": "User",
            "email": "admin@example.com",
            "password": "AdminPassword123!",
        }
        
        # 1. Create first admin - should succeed
        response = self.client.post(self.create_admin_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], Profile.Role.ADMIN)
        
        # 2. Try creating another admin - should fail (403)
        data2 = {**data, "email": "admin2@example.com"}
        response2 = self.client.post(self.create_admin_url, data2)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)
        
        # 3. Check SystemSetting flag
        setting = SystemSetting.load()
        self.assertFalse(setting.is_admin_creation_enabled)

    def test_me_endpoint_requires_auth(self):
        """Verify /api/users/me/ is protected."""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_endpoint_returns_correct_user(self):
        """Verify /api/users/me/ returns the logged-in user's data."""
        user = User.objects.create_user(username="me@example.com", email="me@example.com", password="password")
        Profile.objects.create(user=user, role=Profile.Role.ANALYST)
        
        self.client.force_authenticate(user=user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "me@example.com")
        self.assertEqual(response.data["role"], Profile.Role.ANALYST)

    def test_assign_role_permission_and_self_demotion_guard(self):
        """Test that only ADMIN can assign roles and cannot demote themselves."""
        admin_user = User.objects.create_user(username="admin@ex.com", email="admin@ex.com", password="pass")
        Profile.objects.create(user=admin_user, role=Profile.Role.ADMIN)
        
        target_user = User.objects.create_user(username="target@ex.com", email="target@ex.com", password="pass")
        Profile.objects.create(user=target_user, role=Profile.Role.VIEWER)
        
        assign_url = reverse("users:assign-role", kwargs={"user_id": target_user.pk})
        self.client.force_authenticate(user=admin_user)
        
        # 1. Success: Admin changes target to ANALYST
        response = self.client.patch(assign_url, {"role": Profile.Role.ANALYST})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target_user.profile.refresh_from_db()
        self.assertEqual(target_user.profile.role, Profile.Role.ANALYST)
        
        # 2. Guard: Admin tries to change their own role
        self_assign_url = reverse("users:assign-role", kwargs={"user_id": admin_user.pk})
        response = self.client.patch(self_assign_url, {"role": Profile.Role.VIEWER})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        admin_user.profile.refresh_from_db()
        self.assertEqual(admin_user.profile.role, Profile.Role.ADMIN)


class ThrottlingTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("users:register")

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
            "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
            "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
            "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
            "PAGE_SIZE": 10,
            "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
            "DEFAULT_THROTTLE_RATES": {"anon": "2/day"},
        }
    )
    def test_anon_throttle_limit(self):
        """Verify that anonymous requests are throttled after exceeding the limit."""
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "throttle@example.com",
            "password": "Password123!",
        }
        
        # 1. First request - OK
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Second request - OK
        data["email"] = "throttle2@example.com"
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 3. Third request - Throttled (429)
        data["email"] = "throttle3@example.com"
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
