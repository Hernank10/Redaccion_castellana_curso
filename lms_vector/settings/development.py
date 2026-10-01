# -*- coding: utf-8 -*-
"""development.py - Settings para desarrollo local."""
from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# SQLite local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# En desarrollo NO usar WhiteNoise (Django sirve estaticos)
MIDDLEWARE = [m for m in MIDDLEWARE if 'whitenoise' not in m]

# Sin HTTPS obligatorio
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False