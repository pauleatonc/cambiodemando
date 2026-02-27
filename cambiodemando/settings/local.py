"""
Local development settings (optional).
Use when running outside Docker with local DB or SQLite.
"""
import os

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-local-dev-key-change-in-production',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
