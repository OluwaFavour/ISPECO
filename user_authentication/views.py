from django.contrib.auth import login

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from drf_spectacular.utils import extend_schema
from .serializers import (
    UserSerializer,
    UserUpdateSerializer,
    EmailAuthTokenSerializer,
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

    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses={status.HTTP_201_CREATED: UserSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
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
    serializer_class = UserSerializer

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
        put(request, *args, **kwargs): Handles the HTTP PUT request for updating user details.
            It validates the request data, updates the user details, and returns the response.

    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserUpdateSerializer

    @extend_schema(
        responses={status.HTTP_200_OK: UserSerializer},
    )
    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={status.HTTP_200_OK: UserSerializer},
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

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password updated successfully."}, status=status.HTTP_200_OK
        )
