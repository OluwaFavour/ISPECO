from rest_framework import serializers

from .forms import AddCameraForm
from .models import Camera


class AddCameraSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    ip_address = serializers.IPAddressField()
    port = serializers.IntegerField()
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


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ["id", "name", "ip_address", "port", "model"]
