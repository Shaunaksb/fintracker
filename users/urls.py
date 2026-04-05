from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

from .views import AssignRoleView, CreateAdminView, DisableAdminView, RegisterView

app_name = "users"

urlpatterns = [
    # Auth
    path("register/", RegisterView.as_view(), name="register"),
    path("create-admin/", CreateAdminView.as_view(), name="create-admin"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token-blacklist"),
    # Admin-only management
    path("admin/toggle-creation/", DisableAdminView.as_view(), name="toggle-admin-creation"),
    path("<int:user_id>/assign-role/", AssignRoleView.as_view(), name="assign-role"),
]
