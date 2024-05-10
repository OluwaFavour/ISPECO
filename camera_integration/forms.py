from django import forms
from django.core.validators import URLValidator

from .models import Camera


class AddCameraForm(forms.ModelForm):
    """
    Form for adding a new camera.
    """

    url = forms.URLField(
        validators=[
            URLValidator(schemes=["http", "https", "rtsp", "rtmp", "rtsps", "rtspu"])
        ],
        help_text="Enter the URL of the camera stream. usually in this format rtsp://[username:password@]ip_address[:rtsp_port]/server_URL[[?param1=val1[?param2=val2]…[?paramN=valN]]",
    )
    password = forms.CharField(max_length=100, widget=forms.PasswordInput())

    class Meta:
        model = Camera
        fields = ["name", "ip_address", "url", "password", "port", "model", "user"]

    def save(self, commit=True):
        camera = super().save(commit=False)
        if "user" not in self.cleaned_data:
            raise ValueError("User must be set before saving the form.")
        camera.user = self.cleaned_data["user"]
        camera.url = self.cleaned_data["url"]
        camera.password = self.cleaned_data["password"]
        if commit:
            camera.save()
        return camera
