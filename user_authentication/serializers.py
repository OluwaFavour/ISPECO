from django.contrib.auth import authenticate
from .forms import CustomUserCreationForm
from .models import User, OTP
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField


class LoginOutSerializer(serializers.Serializer):
    expiry = serializers.DateTimeField()
    token = serializers.CharField()


class UserOutSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(max_length=300)
    email = serializers.EmailField()
    country = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=300)
    zip_code = serializers.CharField(max_length=10)
    phone_number = PhoneNumberField()


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class EmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate_email(self, value):
        if not OTP.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email address does not exist.")
        return value

    def validate_otp(self, value):
        if not OTP.objects.filter(otp=value).exists():
            raise serializers.ValidationError("Invalid OTP.")
        return value


class PhoneSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()


class PhoneOTPSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    otp = serializers.CharField(max_length=6)

    def validate_phone_number(self, value):
        if not OTP.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number does not exist.")
        return value

    def validate_otp(self, value):
        if not OTP.objects.filter(otp=value).exists():
            raise serializers.ValidationError("Invalid OTP.")
        return value


class UserInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    password1 = serializers.CharField(
        max_length=128, write_only=True, style={"input_type": "password"}
    )
    password2 = serializers.CharField(
        max_length=128, write_only=True, style={"input_type": "password"}
    )

    def validate_otp(self, value):
        if not OTP.objects.filter(otp=value).exists():
            raise serializers.ValidationError("Invalid OTP.")
        else:
            otp = OTP.objects.get(otp=value)
            if not otp.is_valid():
                raise serializers.ValidationError("OTP has expired.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email address already exists.")
        return value

    def validate(self, data):
        email = data["email"]
        otp = data["otp"]
        if not OTP.objects.filter(email=email, otp=otp).exists():
            raise serializers.ValidationError("Invalid OTP.")
        form = CustomUserCreationForm(data)
        if not form.is_valid():
            raise serializers.ValidationError(form.errors.as_data())
        return data

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password1"]
        user = User.objects.create_user(
            email=email,
            password=password,
        )
        return user


class UserUpdateInSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=300)
    country = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=300)
    zip_code = serializers.CharField(max_length=10)
    phone_number = PhoneNumberField()

    def update(self, instance, validated_data):
        instance.full_name = validated_data.get("full_name", instance.full_name)
        instance.country = validated_data.get("country", instance.country)
        instance.city = validated_data.get("city", instance.city)
        instance.address = validated_data.get("address", instance.address)
        instance.zip_code = validated_data.get("zip_code", instance.zip_code)
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.save()
        return instance


class UserUpdateOutSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(max_length=300)
    country = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=300)
    zip_code = serializers.CharField(max_length=10)
    phone_number = PhoneNumberField()


class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"), style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )
            print(user)
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class PasswordUpdateSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        label=_("Old Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    new_password1 = serializers.CharField(
        label=_("New Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    new_password2 = serializers.CharField(
        label=_("New Password confirmation"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        user = self.context["request"].user
        old_password = attrs.get("old_password")
        new_password1 = attrs.get("new_password1")
        new_password2 = attrs.get("new_password2")

        if not user.check_password(old_password):
            raise serializers.ValidationError(
                {"old_password": _("Wrong password.")}, code="authorization"
            )

        if new_password1 != new_password2:
            raise serializers.ValidationError(
                {"new_password2": _("The two password fields didn't match.")},
                code="authorization",
            )

        return attrs

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password1"])
        user.save()
        user.auth_token_set.all().delete()  # Delete all existing tokens
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email address does not exist.")
        return value

    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        return user


class PasswordResetSerializer(serializers.Serializer):
    password1 = serializers.CharField(
        label=_("New Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    password2 = serializers.CharField(
        label=_("New Password confirmation"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")

        if password1 != password2:
            raise serializers.ValidationError(
                {"password2": _("The two password fields didn't match.")},
                code="authorization",
            )

        return attrs

    def save(self, user):
        user.set_password(self.validated_data["password1"])
        user.save()
        return user
