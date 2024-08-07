from django.urls import path

from .views import (
    CameraListCreateView,
    CameraRetrieveUpdateDestroyView,
    CameraStreamUrlView,
    CameraAuthenticationDetailsRetrieveView,
)

urlpatterns = [
    path("", CameraListCreateView.as_view(), name="camera-list-create"),
    path("<int:id>/", CameraRetrieveUpdateDestroyView.as_view(), name="camera-detail"),
    path("<int:id>/url/", CameraStreamUrlView.as_view(), name="camera-url"),
    path(
        "<int:id>/authentication/",
        CameraAuthenticationDetailsRetrieveView.as_view(),
        name="camera-authentication",
    ),
]
