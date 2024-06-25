#!/bin/sh

# List of required environment variables
required_env_vars=(
    "SECRET_KEY"
    "DATABASE_URL"
    "EMAIL_HOST_PASSWORD"
    "FERNET_KEY"
    "SUPERUSER_PASSWORD"
    "TWILIO_ACCOUNT_SID"
    "TWILIO_AUTH_TOKEN"
    "TWILIO_PHONE_NUMBER"
    "PAYPAL_CLIENT_ID"
    "PAYPAL_SECRET"
    "ISPECO_SERVER_URL"
    "EMAIL_HOST"
    "EMAIL_HOST_USER"
    "EMAIL_PORT"
    "EMAIL_USE_TLS"
    "DEFAULT_FROM_EMAIL"
    "SERVER_EMAIL"
)

# Check if all required environment variables are set
for env_var in "${required_env_vars[@]}"; do
    if [ -z "${!env_var}" ]; then
        echo "Error: Environment variable $env_var is not set."
        exit 1
    fi
done

# Set other environment variables
export ALLOWED_HOSTS='*'
export DJANGO_SETTINGS_MODULE='ISPECO_Core.settings'
export TAG='django'

# Handle migrations and static files
python manage.py collectstatic --noinput
python manage.py makemigrations user_authentication
python manage.py migrate
python manage.py makemigrations camera_integration live_streaming payment
python manage.py migrate
python manage.py create_superuser

# Execute the command passed as arguments to this script
exec "$@"