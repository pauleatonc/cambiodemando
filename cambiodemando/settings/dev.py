"""
Development settings for Docker (docker-compose.yml).
Uses PostgreSQL service 'db'; credentials via environment variables.
"""
import os

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'web', '0.0.0.0']

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-docker-key-change-in-production',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'cambiodemando'),
        'USER': os.environ.get('POSTGRES_USER', 'cambiodemando'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'cambiodemando'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
