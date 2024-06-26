from django.utils import timezone
from django.core.validators import RegexValidator, URLValidator
from rest_framework import serializers

from user_authentication.models import User
from .models import Plan, Subscription, Transaction
from phonenumber_field.serializerfields import PhoneNumberField


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"


class SystemSetUpSerializer(serializers.Serializer):
    # Contact Information
    name = serializers.CharField(max_length=301)
    email = serializers.EmailField()
    phone_number = PhoneNumberField()

    # Time and Date
    date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"])
    time = serializers.TimeField(input_formats=["%I:%M %p"], format="%I:%M %p")

    # Camera Details
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
        ("7mp", "7MP"),
        ("8mp", "8MP"),
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
    number_of_cameras = serializers.IntegerField()
    industry_type = serializers.ChoiceField(choices=INDUSTRY_TYPE_CHOICES)
    camera_type = serializers.ChoiceField(choices=CAMERA_TYPE_CHOICES)
    environment = serializers.ChoiceField(choices=CAMERA_ENVIRONMENT_CHOICES)
    resolution = serializers.ChoiceField(choices=CAMERA_RESOLUTION_CHOICES)
    brand = serializers.ChoiceField(choices=CAMERA_BRAND_CHOICES)
    url = serializers.URLField(
        validators=[URLValidator(schemes=["http", "https", "rtsp"])]
    )

    # Installation Address
    address_line_1 = serializers.CharField(max_length=255)
    address_line_2 = serializers.CharField(
        max_length=255, allow_blank=True, allow_null=True
    )
    city = serializers.CharField(max_length=50)
    zip_code = serializers.CharField(max_length=10)
    state_province = serializers.CharField(max_length=50)
    country = serializers.CharField(max_length=50)
    installation_notes = serializers.CharField(allow_blank=True, allow_null=True)

    def validate(self, data):
        logged_in_user: User = self.context["request"].user
        if logged_in_user.email != data["email"]:
            raise serializers.ValidationError(
                "You can only set up a system for yourself"
            )
        elif logged_in_user.phone_number != data["phone_number"]:
            raise serializers.ValidationError(
                "You can only set up a system for yourself"
            )


class CardSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=300)
    number = serializers.CharField(max_length=19)
    security_code = serializers.CharField(max_length=4)
    expiry_date = serializers.DateField(format="%m/%y", input_formats=["%m/%y"])
    state_province = serializers.CharField(max_length=300)
    city_town = serializers.CharField(max_length=120)
    postal_code = serializers.CharField(max_length=60)
    country_code = serializers.CharField(
        max_length=2, validators=[RegexValidator(r"^([A-Z]{2}|C2)$")]
    )

    def validate_expiry_date(self, value):
        # Check if the expiry date is in the future
        if value < timezone.now().date():
            raise serializers.ValidationError("Card has expired")


class SubscriptionInSerializer(serializers.Serializer):
    system_setup_data = SystemSetUpSerializer()
    card = CardSerializer(required=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    plan = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all())
    quantity = serializers.IntegerField(default=1)
    payment_method = serializers.CharField(max_length=11)

    def validate_payment_method(self, value):
        if value.upper() not in ["CREDIT_CARD", "PAYPAL"]:
            raise serializers.ValidationError("Invalid payment method")
        return value

    def validate_card(self, value):
        if self.initial_data["payment_method"].upper() == "CREDIT_CARD":
            if not value:
                raise serializers.ValidationError("Card details are required")
        return value


class SubscriptionOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
