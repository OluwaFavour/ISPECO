from operator import is_
import random
import secrets
from venv import create
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from phonenumber_field.modelfields import PhoneNumberField


from .managers import UserManager


class InvalidVerificationTokenError(Exception):
    pass


class EmailAlreadyVerifiedError(Exception):
    pass


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        _("email address"),
        unique=True,
        help_text=_(
            "Required. Make sure it is a valid email address. It will be used for logging in."
        ),
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    full_name = models.CharField(_("full name"), max_length=301, blank=True)
    country = models.CharField(_("country"), max_length=100, blank=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    address = models.CharField(_("address"), max_length=300, blank=True)
    zip_code = models.CharField(_("zip code"), blank=True, null=True, max_length=10)
    phone_number = PhoneNumberField(_("phone number"), blank=True, null=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    password_reset_token = models.CharField(
        _("password reset token"), blank=True, null=True, max_length=150
    )
    password_reset_token_created_at = models.DateTimeField(
        _("token created at"), blank=True, null=True
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    objects = UserManager()

    def generate_password_reset_token(self):
        """
        Generate a unique password reset token for the user.
        """
        token = secrets.token_hex(16)
        self.password_reset_token = token
        self.password_reset_token_created_at = timezone.now()
        self.save(
            update_fields=["password_reset_token", "password_reset_token_created_at"]
        )
        return token

    def is_password_reset_token_valid(self):
        if not self.password_reset_token_created_at:
            return False
        expiry_duration = timezone.timedelta(minutes=5)
        expiry_time = self.password_reset_token_created_at + expiry_duration
        return timezone.now() <= expiry_time

    def send_password_reset_email(self, password_reset_link):
        """
        Send a password reset email to the user.
        """
        subject = "Password Reset"
        html_message = render_to_string(
            "password_reset_email.html",
            {"password_reset_link": password_reset_link},
        )
        plain_message = strip_tags(html_message)
        to = self.email
        send_mail(
            subject,
            plain_message,
            from_email=None,
            recipient_list=[to],
            html_message=html_message,
        )

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        return self.full_name

    def get_short_name(self):
        """Return the short name for the user."""
        return self.full_name


class OTP(models.Model):
    email = models.EmailField(_("email address"), blank=True, null=True)
    phone_number = PhoneNumberField(_("phone number"), blank=True, null=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    _is_verified = models.BooleanField(
        default=False
    )  # Added field to store verification status

    @property
    def is_verified(self) -> bool:
        """
        Returns whether the OTP has been verified or not.

        Returns:
            bool: True if the OTP has been verified, False otherwise.
        """
        return self._is_verified

    @is_verified.setter
    def is_verified(self, value: bool) -> None:
        self._is_verified = value

    def __str__(self):
        return self.otp

    def is_valid(self):
        expiry_duration = timezone.timedelta(minutes=5)
        expiry_time = self.created_at + expiry_duration
        return timezone.now() <= expiry_time

    def is_eligible_for_renewal(self):
        expiry_duration = timezone.timedelta(minutes=1)
        expiry_time = self.created_at + expiry_duration
        return timezone.now() >= expiry_time

    def renew(self):
        self.otp = str(random.randint(100000, 999999))
        self.created_at = timezone.now()
        self.save(update_fields=["otp", "created_at"])
        return self.otp


class TemporaryUserUpdateData(models.Model):
    full_name = models.CharField(_("full name"), max_length=301, blank=True)
    country = models.CharField(_("country"), max_length=100, blank=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    address = models.CharField(_("address"), max_length=300, blank=True)
    zip_code = models.CharField(_("zip code"), blank=True, null=True, max_length=10)
    phone_number = PhoneNumberField(_("phone number"), blank=True, null=True)
    user = models.OneToOneField(
        to=User, on_delete=models.CASCADE, related_name="temp_data"
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def is_expired(self):
        expiry_duration = timezone.timedelta(minutes=5)
        expiry_time = self.created_at + expiry_duration
        return timezone.now() > expiry_time


class UserAccess(models.Model):
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
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accesses")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="granted_accesses"
    )
    user_role = models.CharField(
        _("user role"), max_length=10, choices=USER_ROLE_CHOICES
    )
    camera_access = models.CharField(
        _("camera access"), max_length=10, choices=CAMERA_ACCESS_CHOICES
    )
    notification_access = models.CharField(
        _("notification access"), max_length=3, choices=NOTIFICATION_ACCESS_CHOICES
    )

    class Meta:
        unique_together = ("owner", "user")

    def __str__(self):
        return f"{self.user.email} - {self.user_role}"


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(_("title"), max_length=100)
    message = models.TextField(_("message"))
    is_read = models.BooleanField(_("is read"), default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.email} - {self.title}"
