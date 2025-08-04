import os
from decouple import config
from pathlib import Path
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# Uporaba os.path.join, da zagotovimo delovanje na različnih operacijskih sistemih
STATIC_URL = '/static/'
STATIC_ROOT = '/app/static_root' # To bo mapa, kamor bo collectstatic zbral datoteke

# ... ostale nastavitve

SECRET_KEY = config('SECRET_KEY', default='@yotrutest1267uz_k8554.*GC')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

CSRF_TRUSTED_ORIGINS = ['https://vin-obd-search.up.railway.app']

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True

# Dovoljeni gostitelji za lokalni razvoj in Railway
# Uporaba okoljskih spremenljivk, ki se na Railwayu preberejo samodejno.
# Na lokalnem okolju, če ni nastavljeno, bo privzeto 'localhost', '127.0.0.1'
ALLOWED_HOSTS_STR = config('ALLOWED_HOSTS', default='127.0.0.1,localhost')
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'vin-obd-search.up.railway.app']


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
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
# Konfiguracija baze podatkov za lokalno in produkcijsko okolje.
# Če je okoljska spremenljivka DATABASE_URL nastavljena (kot na Railwayu),
# se bo uporabila. Sicer se bo uporabila lokalna konfiguracija.
try:
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL')
        )
    }
except ImproperlyConfigured:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'avto_net_db',
            'USER': 'josko',
            'PASSWORD': '196Guer',
            'HOST': 'localhost',
            'PORT': '5432',
        }
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