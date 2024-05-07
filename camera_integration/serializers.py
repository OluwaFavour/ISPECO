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
