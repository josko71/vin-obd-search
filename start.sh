#!/bin/bash

# Preveri, ali je PORT nastavljen in mu določi privzeto vrednost, če ni
PORT=${PORT:-8000}

# Uveljavite migracije
echo "Applying database migrations..."
python manage.py migrate

# Zberite statične datoteke
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Zaženite Gunicorn strežnik
echo "Starting Gunicorn server..."
exec gunicorn avto_vin_obd_projekt.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 120 \
    --preload