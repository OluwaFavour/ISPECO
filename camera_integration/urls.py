from django.urls import path

from .views import (
    CameraView,
    ListCameraView,
    CameraStreamUrlView,
    CameraCreateView,
)

urlpatterns = [
    path("", CameraCreateView.as_view(), name="add-camera"),
    path("<int:id>/", CameraView.as_view(), name="camera"),
    path("<int:id>/url/", CameraStreamUrlView.as_view(), name="camera-url"),
    path("list/", ListCameraView.as_view(), name="list-cameras"),
]
