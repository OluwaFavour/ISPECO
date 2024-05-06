from django.contrib import admin

from .models import Camera


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ("name", "ip_address", "port", "username", "model", "user")
    search_fields = ("name", "ip_address", "username", "model")
    list_filter = ("model", "user")
