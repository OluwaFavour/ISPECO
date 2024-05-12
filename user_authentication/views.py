from django.contrib.auth import login
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from knox.views import LoginView as KnoxLoginView
from drf_spectacular.utils import extend_schema, inline_serializer
from drf_spectacular.types import OpenApiTypes
from .models import User, EmailAlreadyVerifiedError, InvalidVerificationTokenError
from .serializers import (
    LoginOutSerializer,
    PasswordResetSerializer,
    UserInSerializer,
    UserOutSerializer,
    UserUpdateInSerializer,
    UserUpdateOutSerializer,
    EmailAuthTokenSerializer,
    ForgotPasswordSerializer,
    PasswordUpdateSerializer,
)


class SignupView(generics.GenericAPIView):
    """
    View for user signup.

    This view allows users to sign up by providing their username and email.
    Upon successful signup, a new user will be created and a success response will be returned.

    Methods:
        post(request, *args, **kwargs): Handles the POST request for user signup.

    Attributes:
        serializer_class: The serializer class used for validating and deserializing the request data.
        permission_classes: The permission classes applied to the view.

    """

    serializer_class = UserInSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=UserInSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiTypes.STR,
            400: OpenApiTypes.STR,
        },
        description="Create a new user and send a verification email to the user's email address using the email set as DEFAULT_FROM_EMAIL in the settings as the sender.",
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = user.generate_email_verification_token()
            verification_link = request.build_absolute_uri(
                reverse("verify_email", kwargs={"token": token})
            )
            # Send token to user's email in form of a link
            self.send_verification_email(user, verification_link=verification_link)
            return Response(
                "Please verify your email address", status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_email(self, user, verification_link):
        subject = "Verify your email address"
        html_message = render_to_string(
            "email_verification.html", {"verification_link": verification_link}
        )
        plain_message = strip_tags(html_message)
        to = user.email
        print(f"Sending verification email to {to}")
        send_mail(
            subject,
            plain_message,
            from_email=None,
            recipient_list=[to],
            html_message=html_message,
        )
        print(f"Verification email sent to {to}")


class VerifyEmailView(generics.GenericAPIView):
    """
    View for verifying user email.

    This view allows users to verify their email address by clicking on the verification link
    sent to their email. Upon successful verification, the user's email will be marked as verified
    and a success response will be returned.

    Methods:
        get(request, *args, **kwargs): Handles the GET request for verifying user email.

    Attributes:
        permission_classes: The permission classes applied to the view.

    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="VerifyEmailResponse",
                fields={
                    "message": serializers.CharField(),
                    "user": UserOutSerializer(),
                },
            ),
            400: OpenApiTypes.STR,
        },
        description="Verify the user's email address using the verification token.",
    )
    def get(self, request, *args, **kwargs):
        token = kwargs.get("token")
        user = User.objects.get(email_verification_token=token)
        if user:
            try:
                user.verify_email()
            except EmailAlreadyVerifiedError as e:
                return Response(f"{str(e)}", status=status.HTTP_400_BAD_REQUEST)
            except InvalidVerificationTokenError as e:
                user.delete()
                return Response(f"{str(e)}", status=status.HTTP_400_BAD_REQUEST)
            serializer = UserInSerializer(user)
            return Response(
                {"message": "Email verified successfully", "user": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)


class LoginView(KnoxLoginView):
    """
    View for user login.

    This view allows users to authenticate and log in to the system.
    It inherits from the KnoxLoginView class and overrides the post method
    to handle the login functionality.

    Attributes:
        permission_classes (tuple): A tuple of permission classes that
            determine who can access this view. In this case, it allows
            any user to access the view.

    Methods:
        post(request, format=None): Handles the HTTP POST request for user login.
            It validates the authentication token, logs in the user, and returns
            the response from the parent class's post method.

    """

    permission_classes = (permissions.AllowAny,)
    serializer_class = EmailAuthTokenSerializer

    @extend_schema(
        request=EmailAuthTokenSerializer,
        responses={
            status.HTTP_200_OK: LoginOutSerializer,
            400: OpenApiTypes.STR,
            401: OpenApiTypes.STR,
        },
        description="Authenticate the user and log in to the system. The user must have a verified email address.",
    )
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        if not user.is_email_verified:
            return Response(
                {"detail": "Please verify your email address before logging in."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class UserView(generics.RetrieveAPIView):
    """
    View for retrieving user details.

    This view allows users to retrieve their own details after authentication.
    It inherits from the RetrieveAPIView class and overrides the get_object method
    to return the authenticated user.

    Attributes:
        permission_classes (tuple): A tuple of permission classes that
            determine who can access this view. In this case, it requires
            the user to be authenticated.

    Methods:
        get_object(): Retrieves the authenticated user object.

    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserOutSerializer

    @extend_schema(
        responses={status.HTTP_200_OK: UserOutSerializer},
        description="Retrieve the details of the authenticated user.",
    )
    def get_object(self):
        return self.request.user


class UpdateUserView(generics.GenericAPIView):
    """
    View for updating user details.

    This view allows users to update their own details after authentication.
    It inherits from the GenericAPIView class and overrides the put method
    to handle the update functionality.

    Attributes:
        permission_classes (tuple): A tuple of permission classes that
            determine who can access this view. In this case, it requires
            the user to be authenticated.

    Methods:
        patch(request, *args, **kwargs): Handles the HTTP PUT request for updating user details.
            It validates the request data, updates the user details, and returns the response.

    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserUpdateInSerializer

    @extend_schema(
        responses={status.HTTP_200_OK: UserUpdateOutSerializer},
        description="Partially update the details of the authenticated user.",
    )
    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserPasswordView(generics.GenericAPIView):
    """
    View for updating user password.

    This view allows users to update their password after authentication.
    It inherits from the GenericAPIView class and overrides the put method
    to handle the password update functionality.

    Attributes:
        permission_classes (tuple): A tuple of permission classes that
            determine who can access this view. In this case, it requires
            the user to be authenticated.

    Methods:
        put(request, *args, **kwargs): Handles the HTTP PUT request for updating user password.
            It validates the request data, updates the user password, and returns the response.

    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PasswordUpdateSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="PasswordUpdateResponse",
                fields={"detail": serializers.CharField()},
            )
        },
        description="Update the password of the authenticated user.",
    )
    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password updated successfully. Logged out of all clients."},
            status=status.HTTP_200_OK,
        )


class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ForgotPasswordSerializer

    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={
            status.HTTP_200_OK: OpenApiTypes.STR,
            400: OpenApiTypes.STR,
        },
        description="Send a password reset link to the user's email address using the email set as DEFAULT_FROM_EMAIL in the settings as the sender.",
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = user.generate_password_reset_token()
            reset_link = request.build_absolute_uri(
                reverse("password_reset", kwargs={"token": token})
            )
            user.send_password_reset_email(reset_link)
            return Response(
                "Password reset link sent to your email address",
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PasswordResetSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="PasswordResetResponse", fields={"token": serializers.CharField()}
            ),
            400: OpenApiTypes.STR,
        },
        description="Check if the password reset token specified in the URL is valid and return the token if it is valid.",
    )
    def get(self, request, *args, **kwargs):
        token = kwargs.get("token")
        try:
            user = User.objects.get(password_reset_token=token)
        except User.DoesNotExist:
            return Response(
                {"message": "Invalid password reset token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.is_password_reset_token_valid():
            return Response(
                {"token": token},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "Invalid password reset token"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        request=PasswordResetSerializer,
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="PasswordResetResponsePost",
                fields={"message": serializers.CharField()},
            ),
            400: inline_serializer(
                name="PasswordResetResponseError",
                fields={"message": serializers.CharField()},
            ),
        },
        description="Reset the user's password using the password reset token specified in the URL and update the user's password.",
    )
    def post(self, request, *args, **kwargs):
        token = kwargs.get("token")
        try:
            user = User.objects.get(password_reset_token=token)
        except User.DoesNotExist:
            return Response(
                {"message": "Invalid password reset token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_password_reset_token_valid():
            serializer = self.get_serializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user)
            user.password_reset_token = None
            user.password_reset_token_created_at = None
            user.save()
            return Response(
                {"message": "Password reset successfully"}, status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Invalid password reset token"},
            status=status.HTTP_400_BAD_REQUEST,
        )
