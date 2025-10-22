"""
Configuración WSGI para Sistema de Agendamiento de Citas.
Expone la aplicación WSGI para servidores web de producción (Gunicorn, uWSGI).
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')

application = get_wsgi_application()
