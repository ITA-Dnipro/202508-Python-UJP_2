from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import UserProfile
# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    model = UserProfile

    list_display = ("username", "email", "first_name", "last_name", "user_phone", "is_staff", "updated_at")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_phone', 'updated_at')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("user_phone",)}),
    )

    readonly_fields = ("updated_at",)
