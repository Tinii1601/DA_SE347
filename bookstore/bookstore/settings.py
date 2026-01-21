"""
Django settings for bookstore project.
"""

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

from pathlib import Path
import os
from dotenv import load_dotenv
from decouple import config, Csv  

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')  # Load environment variables from .env file explicitly


# ================== BẢO MẬT – DÙNG .env ==================
SECRET_KEY = config('SECRET_KEY') 
DEBUG = config('DEBUG', default=False, cast=bool)
GEMINI_API_KEY = config('GEMINI_API_KEY', default=None)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='localhost,127.0.0.1')

# ================== APPLICATIONS ==================
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'ckeditor_uploader',
    'import_export',

    # Local apps
    'core',
    'books',
    'users',
    'orders',
    'reviews',
    'payment',
    'chatbot',

    # login social
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'django_unused_media',
    'django_cleanup.apps.CleanupConfig',
]
SITE_ID = 1

# Optional: Jazzmin configuration. Tweak these to taste.
JAZZMIN_SETTINGS = {
    "site_title": "Bookstore Admin",
    "site_header": "Bookstore",
    "welcome_sign": "Welcome to Bookstore admin",
    "show_ui_builder": False,
    "topmenu_links": [
        {"name": "Return to site", "url": "/", "new_window": False},
    ],
}

# Optional UI tweaks for Jazzmin
JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "navbar_small_text": False,
    "body_small_text": False,
    "brand_colour": "#175229",
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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

# ================== DEFAULT AUTO FIELD ==================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================== PAYOS PAYMENT CONFIG ==================
PAYOS_CLIENT_ID = os.getenv('PAYOS_CLIENT_ID', default='').strip()
PAYOS_API_KEY = os.getenv('PAYOS_API_KEY', default='').strip()
PAYOS_CHECKSUM_KEY = os.getenv('PAYOS_CHECKSUM_KEY', default='').strip()

MOMO_NOTIFY_URL = os.getenv('MOMO_NOTIFY_URL', default='http://127.0.0.1:8000/orders/momo/notify/')

# ================== EMAIL CONFIGURATION ==================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'nguyenthikimngoc1402@gmail.com'
EMAIL_HOST_PASSWORD = 'jpqq jock xbky hheu'

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Load ALLOWED_HOSTS from .env, default to localhost
# Lấy từ file .env, nếu không có thì mặc định là localhost
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')

CONTACT_EMAIL = config('CONTACT_EMAIL', default='nguyenthikimngoc1402@gmail.com')

SOCIALACCOUNT_LOGIN_ON_GET = True

# ================== SOCIAL ACCOUNT CONFIG ==================
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET', ''),
            'key': ''
        }
    },
    'facebook': {
        'METHOD': 'oauth2',
        'APP': {
            'client_id': os.getenv('FACEBOOK_CLIENT_ID', ''),
            'secret': os.getenv('FACEBOOK_CLIENT_SECRET', ''),
            'key': ''
        }
    }
}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")