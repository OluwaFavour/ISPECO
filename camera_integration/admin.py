from django.contrib import admin

from .forms import AddCameraForm
from .models import Camera, CameraSetup


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
    )
    list_filter = (
        "brand",
        "camera_type",
        "resolution",
        "industry_type",
        "user",
        "environment",
    )
    ordering = ("brand", "camera_type")


@admin.register(CameraSetup)
class CameraSetupAdmin(admin.ModelAdmin):
    list_display = (
        "camera",
        "installation_notes",
        "address_line_1",
        "city",
        "zip_code",
        "state_province",
        "country",
        "date",
    )
    search_fields = (
        "camera",
        "city",
        "zip_code",
        "state_province",
        "country",
    )
    list_filter = (
        "camera",
        "city",
        "state_province",
        "country",
        "date",
        "camera__user",
        "time",
        "camera__brand",
        "camera__camera_type",
        "camera__environment",
        "camera__resolution",
        "camera__industry_type",
    )
    ordering = ("camera", "city")
