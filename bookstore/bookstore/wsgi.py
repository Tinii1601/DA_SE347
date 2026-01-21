"""
WSGI config for bookstore project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from pathlib import Path
from dotenv import load_dotenv

# Force load .env file specific to project structure
ENV_PATH = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(ENV_PATH)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')

application = get_wsgi_application()
