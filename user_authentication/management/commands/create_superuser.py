import os

from user_authentication.models import User
from django.core.management.base import BaseCommand
from ISPECO_Core.settings import EMAIL_HOST_USER


class Command(BaseCommand):
    help = "Create a superuser"

    def handle(self, *args, **kwargs):
        email = EMAIL_HOST_USER
        password = os.environ.get("SUPERUSER_PASSWORD")
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS("Superuser created successfully"))
        else:
            self.stdout.write(self.style.WARNING("Superuser already exists"))
