from django.contrib import admin

from .models import Profile, SystemSetting


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__email", "user__first_name", "user__last_name")


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ("pk", "is_admin_creation_enabled")

    def has_add_permission(self, request):
        # Only one singleton record should ever exist
        return not SystemSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
