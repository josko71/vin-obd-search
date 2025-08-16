import os
from pathlib import Path
import dj_database_url
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================
# Osnovne nastavitve
# =============================================================
SECRET_KEY = config('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())
ROOT_URLCONF = 'avto_vin_obd_projekt.urls'
WSGI_APPLICATION = 'avto_vin_obd_projekt.wsgi.application'

# =============================================================
# Aplikacije in Middleware
# =============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vozila',
    'storages',  # Dodano za AWS S3
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

# =============================================================
# Predloge (Templates)
# =============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'), # To je vaša trenutna pot
            os.path.join(BASE_DIR, 'vozila', 'templates'), # Dodajte to vrstico
        ],
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

# =============================================================
# Baza podatkov
# =============================================================
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}

# =============================================================
# Statične datoteke (CSS, JS)
# =============================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# =============================================================
# Medijske datoteke (Slike) - NI NASTAVITEV
# =============================================================

# Medijske nastavitve se zdaj določijo v datotekah dev.py in production.py
# na podlagi okolja.