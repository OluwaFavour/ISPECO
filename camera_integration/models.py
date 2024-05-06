from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from cryptography.fernet import Fernet


class Camera(models.Model):
    """
    Represents a camera model.

    Attributes:
        name (str): The name of the camera.
        ip_address (str): The IP address of the camera.
        port (int): The port number of the camera.
        username (str): The username for accessing the camera.
        password (str): The password for accessing the camera (encrypted).
        encrypted_password (bytes): The encrypted password for accessing the camera.
        model (str): The model of the camera.
        user (User): The user associated with the camera.

    Methods:
        __str__(): Returns a string representation of the camera.
    """

    name = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    encrypted_password = models.BinaryField()
    model = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cameras")

    @property
    def password(self) -> str:
        """
        Decrypts and returns the encrypted password.

        Returns:
            str: The decrypted password.
        """
        fernet = Fernet(settings.FERNET_KEY)
        return fernet.decrypt(self.encrypted_password).decode()

    @password.setter
    def password(self, value: str) -> None:
        """
        Encrypts the given password using Fernet encryption and stores it in the encrypted_password attribute.

        Args:
            value (str): The password to be encrypted.

        Returns:
            None
        """
        fernet = Fernet(settings.FERNET_KEY)
        self.encrypted_password = fernet.encrypt(value.encode())

    def __str__(self) -> str:
        return self.name or f"Camera {self.id} - {self.model}"
