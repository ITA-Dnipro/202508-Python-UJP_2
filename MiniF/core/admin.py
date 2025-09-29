from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import UserProfile
from profiles.models import InvestorProfile, StartupProfile, Industry
from notifications.models import Notification, NotificationType
from projects.models import StartupProject


@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    model = UserProfile

    list_display = ("username", "email", "first_name", "last_name", "user_phone", "is_staff", "updated_at")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")

    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("user_phone", "updated_at")}),)

    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("user_phone",)}),)

    readonly_fields = ("updated_at",)

admin.site.register(StartupProfile)
admin.site.register(StartupProject)
admin.site.register(Industry)
admin.site.register(InvestorProfile)
admin.site.register(Notification)
admin.site.register(NotificationType)