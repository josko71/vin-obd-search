# settings/prod.py (produkcijska nastavitev Django aplikacije)
import os
from .base import *
from decouple import config

SECRET_KEY = config('SECRET_KEY')  # Will be pulled from Railway vars
DEBUG = config('DEBUG', default=False, cast=bool)
PORT = int(os.environ.get('PORT', 8000))  # Railway provides this dynamically
# Produkcijska varnost
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 30 * 24 * 60 * 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Railway specifične nastavitve
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='https://*.railway.app', cast=Csv())
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True   
    )
}
