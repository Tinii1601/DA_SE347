"""
Django settings for bookstore project.
"""

from pathlib import Path
import os
from decouple import config, Csv  

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# ================== BẢO MẬT – DÙNG .env ==================
SECRET_KEY = config('SECRET_KEY') 
DEBUG = config('DEBUG', default=False, cast=bool)

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

    # Local apps
    'core',
    'books',
    'users',
    'orders',
    'reviews',
    'payment',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

# ================== STATIC & MEDIA ==================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  

# ================== AUTHENTICATION ==================
AUTHENTICATION_BACKENDS = [
    'users.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/users/login/'

# ================== SESSION & MESSAGES ==================
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
CART_SESSION_ID = 'cart'

# ================== DEFAULT AUTO FIELD ==================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # ================== MOMO PAYMENT CONFIG ==================
# MOMO_API_ENDPOINT = config('MOMO_API_ENDPOINT', default='https://test-payment.momo.vn/v2/gateway/api/create')
# MOMO_PARTNER_CODE = config('MOMO_PARTNER_CODE', default='')
# MOMO_ACCESS_KEY = config('MOMO_ACCESS_KEY', default='')
# MOMO_SECRET_KEY = config('MOMO_SECRET_KEY', default='')
# MOMO_RETURN_URL = config('MOMO_RETURN_URL', default='http://127.0.0.1:8000/orders/momo/return/')

# ================== PAYOS PAYMENT CONFIG ==================
PAYOS_CLIENT_ID = config('PAYOS_CLIENT_ID', default='')
PAYOS_API_KEY = config('PAYOS_API_KEY', default='')
PAYOS_CHECKSUM_KEY = config('PAYOS_CHECKSUM_KEY', default='')

MOMO_NOTIFY_URL = config('MOMO_NOTIFY_URL', default='http://127.0.0.1:8000/orders/momo/notify/')

# ================== EMAIL CONFIGURATION ==================
# Cấu hình gửi email (Mặc định in ra console để test)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Cấu hình SMTP cho Gmail
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = f"Bookstore <{EMAIL_HOST_USER}>"
DEFAULT_FROM_EMAIL = 'Bookstore <noreply@bookstore.com>'