from django import forms

from .models import Camera


class AddCameraForm(forms.ModelForm):
    """
    Form for adding a new camera.
    """

    password = forms.CharField(max_length=100, widget=forms.PasswordInput())

    class Meta:
        model = Camera
        fields = ["name", "ip_address", "password", "port", "model", "user"]

    def save(self, commit=True):
        camera = super().save(commit=False)
        if "user" not in self.cleaned_data:
            raise ValueError("User must be set before saving the form.")
        camera.user = self.cleaned_data["user"]
        camera.password = self.cleaned_data["password"]
        if commit:
            camera.save()
        return camera
