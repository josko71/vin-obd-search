#!/bin/bash

# Preveri, ali je spremenljivka $PORT nastavljena. Če ni, dodeli privzeto vrednost 8000.
PORT=${PORT:-8000}

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server
echo "Starting Gunicorn server..."
exec gunicorn avto_vin_obd_projekt.wsgi:application --bind "0.0.0.0:$PORT" --workers 3 --timeout 120 --preload