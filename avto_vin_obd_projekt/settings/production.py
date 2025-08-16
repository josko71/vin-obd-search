# settings/production.py
from .base import *
from decouple import config

# ===== Medijske datoteke (Slike) - AWS S3 =====
# Vse nastavitve za medije so zdaj usmerjene na AWS S3.
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_VERIFY = True
AWS_S3_SIGNATURE_VERSION = 's3v4'

# Nastavite Django, da za medije uporablja storitev S3
DEFAULT_FILE_STORAGE = 'storages.backends.s3.S3Storage'

# URL, na katerega Django kaže, da bi našel medijske datoteke
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/ilustracije/"

LOGGING = {
      'version': 1,
      'disable_existing_loggers': False,
      'handlers': {
          'console': {
              'class': 'logging.StreamHandler',
          },
      },
      'loggers': {
          'django': {
              'handlers': ['console'],
              'level': 'INFO',
          },
          'storages': {
              'handlers': ['console'],
              'level': 'DEBUG',
              'propagate': False,
          },
          'boto3': {
              'handlers': ['console'],
              'level': 'DEBUG',
              'propagate': False,
          },
      },
  }