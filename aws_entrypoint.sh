#!/bin/sh

# Handle migrations and static files
python manage.py collectstatic --noinput
python manage.py makemigrations user_authentication
python manage.py migrate
python manage.py makemigrations camera_integration live_streaming payment
python manage.py migrate
python manage.py create_superuser

# Execute the command passed as arguments to this script
exec "$@"