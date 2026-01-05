# core_project/settings.py
"""
Configuración de Django para Sistema de Agendamiento de Citas Médicas.
Soporta desarrollo local y producción en Render.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from django.urls import reverse_lazy

load_dotenv()

# ============================================================================
# 1. CONFIGURACIÓN BÁSICA
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-!!0-8(40=d281g9_(m!9pa51jl$@=bi@r07m7ec7v7u_*bbk=_')

# Detección automática del entorno (producción vs desarrollo)
IS_PRODUCTION = os.getenv('RENDER') == 'true'

if IS_PRODUCTION:
    DEBUG = False
    print("🚀 CONFIGURACIONES DE PRODUCCIÓN (Render) ACTIVADAS")
else:
    DEBUG = True
    print("💻 CONFIGURACIONES DE DESARROLLO LOCAL ACTIVADAS")


# ============================================================================
# 2. HOSTS PERMITIDOS Y SEGURIDAD CSRF
# ============================================================================

ALLOWED_HOSTS = []
CSRF_TRUSTED_ORIGINS = []

if IS_PRODUCTION:
    # 1. Subdominio automático de Render (si existe)
    RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if RENDER_EXTERNAL_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
        # Importante: CSRF necesita el esquema (https://)
        CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')
    
    # 2. Dominio personalizado
    ALLOWED_HOSTS.append('medicalintegral.app')
    ALLOWED_HOSTS.append('www.medicalintegral.app')
    
    # Dominios de confianza para formularios seguros (Login)
    CSRF_TRUSTED_ORIGINS.extend([
        'https://medicalintegral.app',
        'https://www.medicalintegral.app',
    ])
else:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])
    CSRF_TRUSTED_ORIGINS.extend(['http://localhost:8000', 'http://127.0.0.1:8000'])


# ============================================================================
# 3. APLICACIONES Y MIDDLEWARE
# ============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'agendamiento.apps.AgendamientoConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Sirve archivos estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'agendamiento.middleware.SessionSecurityMiddleware',
    'agendamiento.middleware.SessionIntegrityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core_project.urls'
WSGI_APPLICATION = 'core_project.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ============================================================================
# 4. BASE DE DATOS
# ============================================================================

# Producción: PostgreSQL vía DATABASE_URL | Desarrollo: SQLite
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# ============================================================================
# 5. VALIDACIÓN DE CONTRASEÑAS
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'agendamiento.validators.CustomMinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'agendamiento.validators.CustomCommonPasswordValidator'},
    {'NAME': 'agendamiento.validators.CustomNumericPasswordValidator'},
]


# ============================================================================
# 6. INTERNACIONALIZACIÓN
# ============================================================================

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True


# ============================================================================
# 7. ARCHIVOS ESTÁTICOS
# ============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

if IS_PRODUCTION:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ============================================================================
# 8. CONFIGURACIONES ADICIONALES
# ============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = reverse_lazy('agendamiento:login')
LOGIN_REDIRECT_URL = '/'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


# ============================================================================
# 9. SEGURIDAD EN PRODUCCIÓN
# ============================================================================

if IS_PRODUCTION:
    # Cookies seguras (solo HTTPS)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Redirigir HTTP a HTTPS
    SECURE_SSL_REDIRECT = True
    
    # HSTS (HTTP Strict Transport Security) - Forzar HTTPS por 1 año
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Confianza en proxy de Render
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Protecciones generales de seguridad
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSFF = True
X_FRAME_OPTIONS = 'DENY'

# Configuración de sesiones
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SAVE_EVERY_REQUEST = True


# ============================================================================
# 10. CONFIGURACIÓN PARA TESTS
# ============================================================================

if 'test' in sys.argv or os.environ.get('TESTING'):
    print("🔧 CONFIGURACIONES DE TEST ACTIVADAS")
    DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}
    PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']