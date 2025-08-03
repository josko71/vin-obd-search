import os
from decouple import config
from pathlib import Path
import dj_database_url


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ... ostale nastavitve
STATIC_URL = '/static/' # URL za dostop do statičnih datotek
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root') # Mapa, kamor bo collectstatic zbral datoteke

SECRET_KEY = config('SECRET_KEY', default='nek-privzet-kljuc-za-razvoj-ni-varno-za-produkcijo')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Dovoljeni gostitelji za lokalni razvoj in Railway
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.railway.app']

#ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1, .localhost, .railway.app').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vozila',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'avto_vin_obd_projekt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Opcijsko, če imate skupno mapo za templati
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'avto_vin_obd_projekt.wsgi.application'


# Database

DATABASE_URL = config('DATABASE_URL', default='postgres://user:password@host:port/dbname')

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='postgres://user:password@localhost:5432/mydatabase')
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Uporaba os.path.join, da zagotovimo delovanje na različnih operacijskih sistemih
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root') # To bo mapa, kamor bo collectstatic zbral datoteke
STATICFILES_DIRS = []


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# MEDIA files settings
# Ko je DEBUG=False, Django ne streže Media datotek. To bo moral Railway rešiti
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Dodatne varnostne nastavitve za produkcijo (ko je DEBUG=False)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000 # Leto dni
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'