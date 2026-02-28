"""
Django base settings for cambiodemando project.

Common configuration shared by all environments.
SECRET_KEY, DEBUG, ALLOWED_HOSTS and DATABASES are defined per environment.
"""

import os
from pathlib import Path

# Build paths: settings/base.py -> settings/ -> cambiodemando/ -> project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'applications.countdown',
    'applications.poll',
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

ROOT_URLCONF = 'cambiodemando.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cambiodemando.context_processors.google_verification',
            ],
        },
    },
]

WSGI_APPLICATION = 'cambiodemando.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# AdSense
ADSENSE_CLIENT = os.environ.get('ADSENSE_CLIENT', '')
ADSENSE_SLOT_INLINE_TOP = os.environ.get('ADSENSE_SLOT_INLINE_TOP', '')
ADSENSE_SLOT_INLINE_BOTTOM = os.environ.get('ADSENSE_SLOT_INLINE_BOTTOM', '')
ADSENSE_SLOT_RAIL_LEFT = os.environ.get('ADSENSE_SLOT_RAIL_LEFT', '')
ADSENSE_SLOT_RAIL_RIGHT = os.environ.get('ADSENSE_SLOT_RAIL_RIGHT', '')

# Verificación de sitio en Google AdSense (meta tag; valor = content del meta google-site-verification)
GOOGLE_SITE_VERIFICATION = os.environ.get('GOOGLE_SITE_VERIFICATION', '')

# Publicaciones diarias e Instagram
SITE_BASE_URL = os.environ.get('SITE_BASE_URL', 'http://localhost:8000')
PUBLIC_MEDIA_BASE_URL = os.environ.get('PUBLIC_MEDIA_BASE_URL', SITE_BASE_URL)
INSTAGRAM_BASE_URL = os.environ.get('INSTAGRAM_BASE_URL', 'https://graph.facebook.com/v22.0')
INSTAGRAM_ACCESS_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN', '')
INSTAGRAM_IG_USER_ID = os.environ.get('INSTAGRAM_IG_USER_ID', '')
INSTAGRAM_APP_ID = os.environ.get('INSTAGRAM_APP_ID', '')
INSTAGRAM_APP_SECRET = os.environ.get('INSTAGRAM_APP_SECRET', '')
INSTAGRAM_REFRESH_MODE = os.environ.get('INSTAGRAM_REFRESH_MODE', 'facebook_exchange')
INSTAGRAM_REFRESH_THRESHOLD_DAYS = int(os.environ.get('INSTAGRAM_REFRESH_THRESHOLD_DAYS', '7'))
INSTAGRAM_CAPTION_TEMPLATE = os.environ.get(
    'INSTAGRAM_CAPTION_TEMPLATE',
    '¿Cómo vamos? Bien: {good_pct}% | Mal: {bad_pct}% | Resultado: {result_label}',
)
DAILY_POST_HOUR = int(os.environ.get('DAILY_POST_HOUR', '12'))
DAILY_POST_MINUTE = int(os.environ.get('DAILY_POST_MINUTE', '0'))

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
