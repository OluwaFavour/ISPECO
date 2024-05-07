from django.urls import path

from .views import CameraView, ListCameraView, CameraPasswordView

urlpatterns = [
    path("", CameraView.as_view(), name="add-camera"),
    path("<int:id>/", CameraView.as_view(), name="camera"),
    path("<int:id>/password/", CameraPasswordView.as_view(), name="camera-password"),
    path("list/", ListCameraView.as_view(), name="list-cameras"),
]
