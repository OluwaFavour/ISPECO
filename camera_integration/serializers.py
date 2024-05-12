from rest_framework import serializers
from django.core.validators import URLValidator

from .forms import AddCameraForm
from .models import Camera


class CameraOutSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100, required=False)
    username = serializers.CharField(max_length=100)
    ip_address = serializers.IPAddressField()
    port = serializers.IntegerField()
    model = serializers.CharField(max_length=100)


class CameraInSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100, required=False)
    username = serializers.CharField(max_length=100)
    ip_address = serializers.IPAddressField()
    port = serializers.IntegerField()
    url = serializers.URLField(
        validators=[
            URLValidator(schemes=["http", "https", "rtsp", "rtmp", "rtsps", "rtspu"])
        ],
        write_only=True,
    )
    password = serializers.CharField(max_length=100, write_only=True)
    model = serializers.CharField(max_length=100)

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
