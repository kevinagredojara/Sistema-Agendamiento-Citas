"""
Configuración ASGI para Sistema de Agendamiento de Citas.
Expone la aplicación ASGI para servidores asíncronos (Daphne, Uvicorn).
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')

application = get_asgi_application()
