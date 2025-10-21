# core_project/settings.py

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from django.urls import reverse_lazy

# Cargar variables de entorno desde el archivo .env en desarrollo
load_dotenv()

# --- 1. CONFIGURACIÓN BÁSICA ---
BASE_DIR = Path(__file__).resolve().parent.parent

# La SECRET_KEY se lee desde las variables de entorno en producción.
# Para desarrollo local, se usa una clave insegura por defecto.
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-!!0-8(40=d281g9_(m!9pa51jl$@=bi@r07m7ec7v7u_*bbk=_')

# El modo DEBUG se activa solo en desarrollo. En producción (Render) estará en False.
# Se controla con la variable de entorno RENDER (que Render define automáticamente).
IS_PRODUCTION = os.getenv('RENDER') == 'true'

if IS_PRODUCTION:
    DEBUG = False
    print("🚀 CONFIGURACIONES DE PRODUCCIÓN (Render) ACTIVADAS")
else:
    DEBUG = True
    print("💻 CONFIGURACIONES DE DESARROLLO LOCAL ACTIVADAS")


# --- 2. GESTIÓN DE HOSTS (URLS PERMITIDAS) ---
ALLOWED_HOSTS = []

if IS_PRODUCTION:
    # Añadir el host de Render
    RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if RENDER_EXTERNAL_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

    ALLOWED_HOSTS.append('medicalintegral.app')
    ALLOWED_HOSTS.append('www.medicalintegral.app')
else:
    # En desarrollo, permitimos los hosts locales.
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])


# --- 3. APLICACIONES Y MIDDLEWARE ---
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
    # WhiteNoise debe estar justo después de SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
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


# --- 4. BASE DE DATOS (Configuración unificada) ---
# En Render, se usará la variable DATABASE_URL con PostgreSQL.
# En local, se usará una base de datos SQLite por defecto.
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# --- 5. VALIDACIÓN DE CONTRASEÑAS ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'agendamiento.validators.CustomMinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'agendamiento.validators.CustomCommonPasswordValidator'},
    {'NAME': 'agendamiento.validators.CustomNumericPasswordValidator'},
]


# --- 6. INTERNACIONALIZACIÓN ---
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True


# --- 7. ARCHIVOS ESTÁTICOS (CSS, JS, Imágenes) ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Configuración de WhiteNoise para servir estáticos en producción.
if IS_PRODUCTION:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- 8. CONFIGURACIONES ADICIONALES ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = reverse_lazy('agendamiento:login')
LOGIN_REDIRECT_URL = '/'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


# --- 9. CONFIGURACIONES DE SEGURIDAD DE PRODUCCIÓN ---
if IS_PRODUCTION:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    # HSTS Settings (Mejora la seguridad forzando HTTPS)
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Django confía en el proxy de Render (necesario para SECURE_SSL_REDIRECT)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Configuraciones de seguridad generales
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSFF = True
X_FRAME_OPTIONS = 'DENY'

# Configuración de sesiones
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SAVE_EVERY_REQUEST = True

# --- 10. CONFIGURACIONES PARA TESTS ---
# Simplifica la configuración cuando se ejecutan los tests de Django.
if 'test' in sys.argv or os.environ.get('TESTING'):
    print("🔧 CONFIGURACIONES DE TEST ACTIVADAS")
    # Usa una base de datos en memoria para tests más rápidos.
    DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}
    # Simplifica el hashing de contraseñas para acelerar los tests.
    PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']