"""
Django settings for bookstore project.
"""

from pathlib import Path
from dotenv import load_dotenv
from decouple import config, Csv
import dj_database_url

# START PATCH: Fix Jazzmin format_html compatibility with Django 6.0
from django.utils import html
from django.utils.safestring import mark_safe

_original_format_html = html.format_html

def patched_format_html(format_string, *args, **kwargs):
    if not args and not kwargs:
        return mark_safe(format_string)
    return _original_format_html(format_string, *args, **kwargs)

html.format_html = patched_format_html
# END PATCH

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file explicitly
load_dotenv(BASE_DIR / '.env')


# ================== BẢO MẬT & MÔI TRƯỜNG ==================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='127.0.0.1,localhost,.onrender.com')
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv(), default='https://*.onrender.com,http://127.0.0.1,http://localhost')

# API Keys
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')


# ================== APPLICATIONS ==================
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'bookstore.custom_app_configs.CustomAuthConfig',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'ckeditor_uploader',
    'import_export',

    # Local apps
    'core.apps.CoreConfig',
    'books',
    'users',
    'orders',
    'reviews',
    'payment',
    'chatbot',

    # Login social
    'bookstore.custom_app_configs.CustomSitesConfig',
    'allauth',
    'bookstore.custom_app_configs.CustomAccountConfig',
    'bookstore.custom_app_configs.CustomSocialAccountConfig',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'django_unused_media',
    'django_cleanup.apps.CleanupConfig',
]

SITE_ID = 1

# Jazzmin settings
JAZZMIN_SETTINGS = {
    "site_title": "Bookstore Admin",
    "site_header": "Bookstore",
    "welcome_sign": "Welcome to Bookstore admin",
    "show_ui_builder": False,
    "topmenu_links": [
        {"name": "Return to site", "url": "/", "new_window": False},
    ],
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "navbar_small_text": False,
    "body_small_text": False,
    "brand_colour": "#175229",
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'bookstore.urls'


# ================== TEMPLATES ==================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.categories_processor',
                'orders.context_processors.cart',
                'users.context_processors.wishlist_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'bookstore.wsgi.application'


# ================== DATABASE ==================
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ================== PASSWORD VALIDATION ==================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ================== INTERNATIONALIZATION ==================
LANGUAGE_CODE = 'vi-vn'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','


# ================== STATIC & MEDIA ==================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise Production static storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
    }
}


# ================== AUTHENTICATION ==================
AUTHENTICATION_BACKENDS = [
    'users.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/users/login/'


# ================== SESSION & MESSAGES ==================
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
CART_SESSION_ID = 'cart'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ================== PAYOS PAYMENT CONFIG ==================
PAYOS_CLIENT_ID = config('PAYOS_CLIENT_ID', default='').strip()
PAYOS_API_KEY = config('PAYOS_API_KEY', default='').strip()
PAYOS_CHECKSUM_KEY = config('PAYOS_CHECKSUM_KEY', default='').strip()


# ================== MANUAL PAYMENT (VIETQR) ==================
VIETQR_BANK_NAME = config('VIETQR_BANK_NAME', default='BIDV')
VIETQR_BANK_BIN = config('VIETQR_BANK_BIN', default='970418')
VIETQR_ACCOUNT_NAME = config('VIETQR_ACCOUNT_NAME', default='PHAM MINH TIEN')
VIETQR_ACCOUNT_NUMBER = config('VIETQR_ACCOUNT_NUMBER', default='8871946801')
VIETQR_QR_URL = config('VIETQR_QR_URL', default='')


# ================== EMAIL CONFIGURATION ==================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)

EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
CONTACT_EMAIL = config('CONTACT_EMAIL', default=EMAIL_HOST_USER)


# ================== SOCIAL ACCOUNT CONFIG ==================
SOCIALACCOUNT_LOGIN_ON_GET = True

GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')

FACEBOOK_CLIENT_ID = config('FACEBOOK_CLIENT_ID', default='')
FACEBOOK_CLIENT_SECRET = config('FACEBOOK_CLIENT_SECRET', default='')

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET,
            'key': ''
        }
    },
    'facebook': {
        'METHOD': 'oauth2',
        'APP': {
            'client_id': FACEBOOK_CLIENT_ID,
            'secret': FACEBOOK_CLIENT_SECRET,
            'key': ''
        }
    }
}

# Tắt cảnh báo bảo mật của CKEditor 4
SILENCED_SYSTEM_CHECKS = ['ckeditor.W001']