from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "full_name",
                    "country",
                    "city",
                    "address",
                    "zip_code",
                    "phone_number",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "full_name",
                    "country",
                    "city",
                    "address",
                    "zip_code",
                    "phone_number",
                ),
            },
        ),
    )
    list_display = (
        "email",
        "full_name",
        "country",
        "city",
        "address",
        "zip_code",
        "phone_number",
        "is_staff",
        "is_active",
    )
    search_fields = (
        "email",
        "full_name",
        "country",
        "city",
        "address",
        "zip_code",
        "phone_number",
    )
    ordering = (
        "email",
        "full_name",
        "country",
        "city",
        "address",
        "zip_code",
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("email", "phone_number", "otp", "created_at")
    search_fields = ("email", "phone_number", "otp")
    ordering = ("email", "phone_number", "otp")
