# -*- coding: utf-8 -*-
"""production.py - Settings para produccion (PostgreSQL + HTTPS)."""
from .base import *  # noqa
import dj_database_url

DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'temp-key-change-in-railway')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

# PostgreSQL
if os.environ.get('DATABASE_URL'):
    DATABASES = {'default': dj_database_url.config(conn_max_age=600, ssl_require=False)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'vector_db'),
            'USER': os.environ.get('DB_USER', 'vector_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': 60,
        }
    }

# HTTPS obligatorio
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Logging a archivo
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': str(BASE_DIR / 'logs' / 'django.log'),
        },
    },
    'loggers': {
        'django': {'handlers': ['file'], 'level': 'WARNING', 'propagate': True},
    },
}

# ============================================================
# STORAGE EXTERNO (S3 / Cloudflare R2 / Backblaze B2)
# ============================================================
import os

if os.environ.get('AWS_ACCESS_KEY_ID'):
    # Backend S3
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'vector-media')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'auto')
    AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL', None)
    AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN', None)

    AWS_DEFAULT_ACL = None  # Privado por defecto
    AWS_QUERYSTRING_AUTH = True  # URLs firmadas temporales
    AWS_QUERYSTRING_EXPIRE = 3600  # 1 hora
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

    MEDIA_URL = '/media/'  # Se usa para desarrollo; en prod las URLs las genera el storage
    print('Storage externo S3/R2 configurado')
