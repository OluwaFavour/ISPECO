from django.urls import path

from .views import AddCameraView, DeleteCameraView

urlpatterns = [
    path("add/", AddCameraView.as_view(), name="add-camera"),
    path("delete/<int:id>/", DeleteCameraView.as_view(), name="delete-camera"),
]
