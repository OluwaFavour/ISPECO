from django.conf import settings
from django.core.validators import URLValidator
from django.db import models
from user_authentication.models import User

from cryptography.fernet import Fernet


class Camera(models.Model):
    """
    Represents a camera model.

    Attributes:
        user (User): The user who owns the camera.
        camera_type (str): The type of the camera.
        industry_type (str): The industry type the camera is used in.
        environment (str): The environment the camera is used in.
        resolution (str): The resolution of the camera.
        brand (str): The brand of the camera.
        encrypted_url (bytes): The encrypted URL to access the camera stream.

    Methods:
        stream_url: Decrypts and returns the encrypted URL.
        stream_url.setter: Encrypts the given URL using Fernet encryption and stores it in the encrypted_url attribute.
        __str__: Returns a string representation of the camera model.
    """

    CAMERA_ENVIRONMENT_CHOICES = [
        ("indoor", "Indoor"),
        ("outdoor", "Outdoor"),
        ("both", "Both"),
    ]
    CAMERA_TYPE_CHOICES = [
        ("dome", "Dome"),
        ("bullet", "Bullet"),
        ("ptz", "PTZ (Pan-Tilt-Zoom)"),
        ("c_mount", "C-Mount"),
        ("day_night", "Day/Night"),
        ("thermal", "Thermal"),
        ("wireless", "Wireless"),
        ("hd", "High Definition (HD)"),
        ("360", "360-Degree"),
        ("network_ip", "Network/IP"),
    ]
    INDUSTRY_TYPE_CHOICES = [
        ("retail", "Retail"),
        ("restaurant", "Restaurant"),
        ("club", "Club"),
        ("others", "Others"),
    ]
    CAMERA_RESOLUTION_CHOICES = [
        ("1mp", "1MP"),
        ("2mp", "2MP"),
        ("3mp", "3MP"),
        ("4mp", "4MP"),
        ("5mp", "5MP"),
        ("6mp", "6MP"),
        ("7mp", "7MP")("8mp", "8MP"),
    ]
    CAMERA_BRAND_CHOICES = [
        ("samsumg", "Samsung"),
        ("avigilon", "Avigilon"),
        ("honeywell", "Honeywell"),
        ("axiscommunication", "AxisCommunication"),
        ("panasonic", "Panasonic"),
        ("vivotek", "Vivotek"),
        ("alhuatechnology", "AlhuaTechnology"),
        ("hikvision", "HikVision"),
        ("bosch", "Bosch"),
        ("cp_plus", "CP Plus"),
        ("others", "Others"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cameras")
    name = models.CharField(max_length=255, blank=True, null=True)
    camera_type = models.CharField(max_length=50, choices=CAMERA_TYPE_CHOICES)
    industry_type = models.CharField(max_length=50)
    environment = models.CharField(max_length=50, choices=CAMERA_ENVIRONMENT_CHOICES)
    resolution = models.CharField(max_length=50, choices=CAMERA_RESOLUTION_CHOICES)
    brand = models.CharField(max_length=50, choices=CAMERA_BRAND_CHOICES)
    encrypted_url = models.BinaryField(blank=True, null=True)
    # ip_address = models.GenericIPAddressField()
    # port = models.IntegerField()
    # encrypted_password = models.BinaryField()

    # @property
    # def password(self) -> str:
    #     """
    #     Decrypts and returns the encrypted password.

    #     Returns:
    #         str: The decrypted password.
    #     """
    #     fernet = Fernet(settings.FERNET_KEY)
    #     return fernet.decrypt(self.encrypted_password).decode()

    # @password.setter
    # def password(self, value: str) -> None:
    #     """
    #     Encrypts the given password using Fernet encryption and stores it in the encrypted_password attribute.

    #     Args:
    #         value (str): The password to be encrypted.

    #     Returns:
    #         None
    #     """
    #     fernet = Fernet(settings.FERNET_KEY)
    #     self.encrypted_password = fernet.encrypt(value.encode())

    @property
    def stream_url(self) -> str:
        """
        Decrypts and returns the encrypted URL.

        Returns:
            str: The decrypted URL.
        """
        fernet = Fernet(settings.FERNET_KEY)
        return fernet.decrypt(self.encrypted_url).decode()

    @stream_url.setter
    def stream_url(self, value: str) -> None:
        """
        Encrypts the given URL using Fernet encryption and stores it in the encrypted_url attribute.

        Args:
            value (str): The URL to be encrypted.

        Returns:
            None
        """
        fernet = Fernet(settings.FERNET_KEY)
        self.encrypted_url = fernet.encrypt(value.encode())

    def __str__(self) -> str:
        return f"{self.brand} {self.camera_type} ({self.pk})"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"{self.brand} {self.camera_type} ({self.pk})"
        super().save(*args, **kwargs)


class CameraSetup(models.Model):
    """
    Represents the setup details of a camera.

    Attributes:
        camera (Camera): The camera for which the setup details are provided.
        address_line_1 (str): The first line of the address where the camera is installed.
        address_line_2 (str): The second line of the address where the camera is installed.
        city (str): The city where the camera is installed.
        zip_code (str): The ZIP code of the area where the camera is installed.
        state_province (str): The state or province where the camera is installed.
        country (str): The country where the camera is installed.
        installation_notes (str): Additional notes about the installation of the camera.

    Methods:
        __str__: Returns a string representation of the camera setup model.
    """

    camera = models.OneToOneField(
        Camera, on_delete=models.CASCADE, related_name="setup"
    )
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    state_province = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    date = models.DateField()
    time = models.TimeField()
    installation_notes = models.TextField()

    def __str__(self) -> str:
        return f"{self.camera} - {self.address_line_1}, {self.city}, {self.state_province}, {self.country}"
