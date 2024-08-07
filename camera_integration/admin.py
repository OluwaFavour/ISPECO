from django.contrib import admin

from .forms import AddCameraForm
from .models import Camera


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    add_form = AddCameraForm
    form = AddCameraForm
    list_display = (
        "brand",
        "camera_type",
        "environment",
        "resolution",
        "industry_type",
        "encrypted_url",
        "user",
    )
    search_fields = (
        "brand",
        "camera_type",
        "resolution",
        "industry_type",
        "user",
        "environment",
        "city",
        "zip_code",
        "state_province",
        "country",
    )
    list_filter = (
        "brand",
        "camera_type",
        "resolution",
        "industry_type",
        "user",
        "environment",
        "city",
        "state_province",
        "country",
        "created_at",
        "updated_at",
    )
    ordering = ("brand", "camera_type")
