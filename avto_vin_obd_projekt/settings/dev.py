# settings/dev.py
from .base import *

DEBUG = True

# Razvojna baza podatkov
DATABASES = {
    'default': dj_database_url.config(
        default='postgres://josko:196Guer@localhost:5432/avto_net_db',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Odstranite te vrstice:
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = ['127.0.0.1']

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True
}
