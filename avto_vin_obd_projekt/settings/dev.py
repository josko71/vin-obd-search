# settings/dev.py
from .base import *

DEBUG = True

# Razvojna baza podatkov: iz url lahko preberete podatke
# za povezavo z bazo, ki jo uporabljate v razvoju.
DATABASES = {
    'default': dj_database_url.config(
        default='postgres://josko:196Guer@localhost:5432/avto_net_db',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Odstranite ali zakomentiraj te vrstice:
#INSTALLED_APPS += ['debug_toolbar']
#MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
#INTERNAL_IPS = ['127.0.0.1']

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True
}

# ===== Medijske datoteke (Slike) za LOKALNI RAZVOJ =====
# Uporaba lokalnega datotečnega sistema namesto AWS S3.
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Poti do medijskih datotek na lokalnem disku.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"
