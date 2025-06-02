# Azure App Service configuration file
# This file tells Azure how to run your Django application

import os
from .settings import *

# Override settings for Azure deployment
DEBUG = False

# Azure App Service sets this automatically
ALLOWED_HOSTS = [
    os.getenv('WEBSITE_HOSTNAME', 'localhost'),
    'mvpagendamientocitasmedicas.azurewebsites.net',
    '.azurewebsites.net',
]

# Database configuration for Azure (keeping SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files configuration for Azure
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Security settings for Azure
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
