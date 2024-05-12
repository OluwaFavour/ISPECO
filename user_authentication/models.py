import secrets
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


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
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
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
    is_email_verified = models.BooleanField(_("email verified"), default=False)
    email_verification_token = models.CharField(
        _("verification token"), blank=True, null=True, max_length=150
    )
    email_verification_token_created_at = models.DateTimeField(
        _("token created at"), blank=True, null=True
    )
    password_reset_token = models.CharField(
        _("password reset token"), blank=True, null=True, max_length=150
    )
    password_reset_token_created_at = models.DateTimeField(
        _("token created at"), blank=True, null=True
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    REQUIRED_FIELDS = ["first_name", "last_name"]
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

    def generate_email_verification_token(self):
        """
        Generate a unique email verification token for the user.
        """
        token = secrets.token_hex(16)
        self.email_verification_token = token
        self.email_verification_token_created_at = timezone.now()
        self.save(
            update_fields=[
                "email_verification_token",
                "email_verification_token_created_at",
            ]
        )
        return token

    def is_email_verification_token_valid(self):
        if not self.email_verification_token_created_at:
            return False
        expiry_duration = timezone.timedelta(minutes=5)
        expiry_time = self.email_verification_token_created_at + expiry_duration
        return timezone.now() <= expiry_time

    def verify_email(self):
        if self.is_email_verified:
            raise EmailAlreadyVerifiedError("The email is already verified.")
        if not self.is_email_verification_token_valid():
            raise InvalidVerificationTokenError(
                "The email verification token has expired. Sign up again to get a new one."
            )
        self.is_email_verified = True
        self.save(update_fields=["is_email_verified"])
        return self.is_email_verified

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
