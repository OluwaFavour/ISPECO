from django.contrib.auth import login

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from .serializers import UserSignupSerializer


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

    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User created successfully",
                    "user": {"username": user.username, "email": user.email},
                },
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

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return super(LoginView, self).post(request, format=None)
