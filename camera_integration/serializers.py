from rest_framework import serializers
from django.core.validators import URLValidator

from .forms import AddCameraForm
from .models import Camera


class CameraOutSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    camera_type = serializers.CharField()
    industry_type = serializers.CharField()
    environment = serializers.CharField()
    resolution = serializers.CharField()
    brand = serializers.CharField()


class CameraInSerializer(serializers.Serializer):
    CAMERA_ENVIRONMENT_CHOICES = [
        ("indoor", "Indoor"),
        ("outdoor", "Outdoor"),
        ("both", "Both"),
    ]
    CAMERA_TYPE_CHOICES = [
        ("dome", "Dome"),
        ("bullet", "Bullet"),
        ("ptz", "PTZ (Pan-Tilt-Zoom)"),
        ("c_mount", "C-Mount"),
        ("day_night", "Day/Night"),
        ("thermal", "Thermal"),
        ("wireless", "Wireless"),
        ("hd", "High Definition (HD)"),
        ("360", "360-Degree"),
        ("network_ip", "Network/IP"),
    ]
    INDUSTRY_TYPE_CHOICES = [
        ("retail", "Retail"),
        ("restaurant", "Restaurant"),
        ("club", "Club"),
        ("others", "Others"),
    ]
    CAMERA_RESOLUTION_CHOICES = [
        ("1mp", "1MP"),
        ("2mp", "2MP"),
        ("3mp", "3MP"),
        ("4mp", "4MP"),
        ("5mp", "5MP"),
        ("6mp", "6MP"),
        ("7mp", "7MP")("8mp", "8MP"),
    ]
    CAMERA_BRAND_CHOICES = [
        ("samsumg", "Samsung"),
        ("avigilon", "Avigilon"),
        ("honeywell", "Honeywell"),
        ("axiscommunication", "AxisCommunication"),
        ("panasonic", "Panasonic"),
        ("vivotek", "Vivotek"),
        ("alhuatechnology", "AlhuaTechnology"),
        ("hikvision", "HikVision"),
        ("bosch", "Bosch"),
        ("cp_plus", "CP Plus"),
        ("others", "Others"),
    ]

    id = serializers.IntegerField(read_only=True)
    camera_type = serializers.ChoiceField(choices=CAMERA_TYPE_CHOICES)
    industry_type = serializers.ChoiceField(choices=INDUSTRY_TYPE_CHOICES)
    environment = serializers.ChoiceField(choices=CAMERA_ENVIRONMENT_CHOICES)
    resolution = serializers.ChoiceField(choices=CAMERA_RESOLUTION_CHOICES)
    brand = serializers.ChoiceField(choices=CAMERA_BRAND_CHOICES)
    stream_url = serializers.URLField(
        validators=[URLValidator(schemes=["http", "https", "rtsp"])],
        write_only=True,
    )

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        form = AddCameraForm(validated_data)
        if not form.is_valid():
            raise serializers.ValidationError(form.errors)
        camera = form.save()
        return camera

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def partial_update(self, instance, validated_data):
        return self.update(instance, validated_data)
