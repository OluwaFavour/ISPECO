from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password1 = serializers.CharField(max_length=128, write_only=True)
    password2 = serializers.CharField(max_length=128, write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email address already exists.")
        return value

    def validate(self, data):
        form = UserCreationForm(data)
        if not form.is_valid():
            raise serializers.ValidationError(form.errors.as_data())
        return data

    def create(self, validated_data):
        username = validated_data["username"]
        email = validated_data["email"]
        password = validated_data["password1"]
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        return user
