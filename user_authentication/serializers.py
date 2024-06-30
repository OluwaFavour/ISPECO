import email
from django.contrib.auth import authenticate
from .forms import CustomUserCreationForm
from .models import Notification, User, OTP, UserAccess
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField


class LoginOutSerializer(serializers.Serializer):
    expiry = serializers.DateTimeField()
    token = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    pass


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


class UserAccessSerializer(serializers.Serializer):
    USER_ROLE_CHOICES = [
        ("admin", "Admin"),
        ("viewer", "Viewer"),
        ("other", "Other"),
    ]
    CAMERA_ACCESS_CHOICES = [
        ("indoor", "Indoor"),
        ("outdoor", "Outdoor"),
        ("both", "Both"),
    ]
    NOTIFICATION_ACCESS_CHOICES = [("yes", "Yes"), ("no", "No")]
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user_full_name = serializers.CharField(max_length=300)
    user_email = serializers.EmailField()
    user_phone_number = PhoneNumberField()
    user_role = serializers.ChoiceField(choices=USER_ROLE_CHOICES)
    camera_access = serializers.ChoiceField(choices=CAMERA_ACCESS_CHOICES)
    notification_access = serializers.ChoiceField(choices=NOTIFICATION_ACCESS_CHOICES)
    password1 = serializers.CharField(
        max_length=128, write_only=True, style={"input_type": "password"}
    )
    password2 = serializers.CharField(
        max_length=128, write_only=True, style={"input_type": "password"}
    )

    def validate_user_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email address does not exist.")
        return value

    def validate(self, data):
        # Check if passwords match
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError(
                {"password2": _("The two password fields didn't match.")},
                code="authorization",
            )

        # Validate user details
        user_email = data["user_email"]
        user_full_name = data["user_full_name"]
        user_phone_number = data["user_phone_number"]
        if not User.objects.filter(
            email=user_email,
            full_name=user_full_name,
            phone_number=user_phone_number,
        ).exists():
            raise serializers.ValidationError(
                "Invalid user details. Check the email, full name, and phone number."
            )

        # Authenticate user
        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=data["password1"],
        )
        if not user:
            raise serializers.ValidationError(
                "Invalid login credentials.", code="authorization"
            )

        # Check if user already has access to the owner's account
        owner = data["owner"]
        if UserAccess.objects.filter(owner=owner, user=user).exists():
            raise serializers.ValidationError(
                "User already has access to the owner's account.", code="bad_request"
            )
        data["user"] = user

        return data

    def create(self, validated_data):
        owner = validated_data["owner"]
        user = validated_data["user"]
        user_role = validated_data["user_role"]
        camera_access = validated_data["camera_access"]
        notification_access = validated_data["notification_access"]

        user_access = UserAccess.objects.create(
            owner=owner,
            user=user,
            user_role=user_role,
            camera_access=camera_access,
            notification_access=notification_access,
        )
        return user_access

    def update(self, instance, validated_data):
        instance.user_role = validated_data.get("user_role", instance.user_role)
        instance.camera_access = validated_data.get(
            "camera_access", instance.camera_access
        )
        instance.notification_access = validated_data.get(
            "notification_access", instance.notification_access
        )
        instance.save()
        return instance


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        return Notification.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.is_read = validated_data.get("is_read", instance.is_read)
        instance.save()
        return instance
