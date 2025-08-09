#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files (če je potrebno)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server
echo "Starting Gunicorn server..."
exec gunicorn avto_vin_obd_projekt.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3