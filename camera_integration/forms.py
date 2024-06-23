from django import forms
from django.core.validators import URLValidator

from .models import Camera


class AddCameraForm(forms.ModelForm):
    """
    Form for adding a new camera.
    """

    stream_url = forms.URLField(
        validators=[URLValidator(schemes=["http", "https", "rtsp"])],
        help_text="Enter the URL of the camera stream. usually in this format rtsp://[username:password@]ip_address[:rtsp_port]/server_URL[[?param1=val1[?param2=val2]…[?paramN=valN]]",
    )

    class Meta:
        model = Camera
        fields = [
            "brand",
            "camera_type",
            "resolution",
            "industry_type",
            "stream_url",
            "environment",
            "user",
        ]

    def save(self, commit=True):
        camera: Camera = super().save(commit=False)
        if "user" not in self.cleaned_data:
            raise ValueError("User must be set before saving the form.")
        camera.user = self.cleaned_data["user"]
        camera.stream_url = self.cleaned_data["stream_url"]
        if commit:
            camera.save()
        return camera
