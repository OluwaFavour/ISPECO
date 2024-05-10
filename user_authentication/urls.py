from django.urls import path

from knox import views as knox_views
from .views import (
    LoginView,
    SignupView,
    UserView,
    UpdateUserView,
    UserPasswordView,
    VerifyEmailView,
    PasswordResetView,
    ForgotPasswordView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="knox_signup"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("verify-email/<str:token>", VerifyEmailView.as_view(), name="verify_email"),
    path(
        "password-reset/<str:token>", PasswordResetView.as_view(), name="password_reset"
    ),
    path("login/", LoginView.as_view(), name="knox_login"),
    path("logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"),
    path("user/", UserView.as_view(), name="get_user"),
    path("user/update/", UpdateUserView.as_view(), name="update_user"),
    path("user/change-password/", UserPasswordView.as_view(), name="update_password"),
]
