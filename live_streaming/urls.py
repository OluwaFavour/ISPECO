from django.urls import path

from .views import index


urlpatterns = [
    path("<int:cam_id>/", index, name="index"),
]
