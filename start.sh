#!/bin/sh

# Set Django settings module
export DJANGO_SETTINGS_MODULE=avto_vin_obd_projekt.settings.prod

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn server
gunicorn avto_vin_obd_projekt.wsgi:application --bind 0.0.0.0:$PORT