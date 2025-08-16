"""
WSGI config for avto_vin_obd_projekt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

print(f"Loading settings from WSGI: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')}")
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avto_vin_obd_projekt.settings.production')

application = get_wsgi_application()
