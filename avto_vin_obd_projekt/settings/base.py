import os
from pathlib import Path
import dj_database_url
from decouple import config, Csv

ROOT_URLCONF = 'avto_vin_obd_projekt.urls'
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ... (ostale nastavitve, kot so SECRET_KEY, DEBUG, itd.)

# Aplikacije
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vozila',
    'storages', # <--- Pomembno
]

# ... (ostale nastavitve, kot so MIDDLEWARE, TEMPLATES, itd.)

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] # <--- Samo ta vrstica

# Nastavitve za AWS S3
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='eu-central-1')
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True

# Django zdaj uporablja AWS S3 kot privzeti sistem za shranjevanje datotek
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Povemo Djangoju, kakšen bo osnovni URL za medije, ki jih streže AWS.
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/"

# ... (ostala koda)