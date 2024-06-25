#!/bin/sh

# Read secrets from files and export them as environment variables
export SECRET_KEY=$(cat /run/secrets/secret_key)
export DATABASE_URL=$(cat /run/secrets/database_url)
export EMAIL_HOST_PASSWORD=$(cat /run/secrets/email_host_password)
export FERNET_KEY=$(cat /run/secrets/fernet_key)
export SUPERUSER_PASSWORD=$(cat /run/secrets/superuser_password)

# Handle migrations and static files
python manage.py collectstatic --noinput
python manage.py makemigrations user_authentication
python manage.py migrate
python manage.py makemigrations camera_integration live_streaming payment
python manage.py migrate
python manage.py create_superuser

# Execute the command passed as arguments to this script
exec "$@"