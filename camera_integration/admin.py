from django.contrib import admin

from .forms import AddCameraForm
from .models import Camera


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    add_form = AddCameraForm
    form = AddCameraForm
    list_display = ("name", "ip_address", "port", "model", "encrypted_password", "user")
    search_fields = ("name", "ip_address", "model")
    list_filter = ("model", "user")
    ordering = ("name",)
