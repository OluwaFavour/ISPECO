from django.urls import path

from knox import views as knox_views
from .views import LoginView, SignupView, UserView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="knox_signup"),
    path("login/", LoginView.as_view(), name="knox_login"),
    path("logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"),
    path("user/", UserView.as_view(), name="get_user"),
]
