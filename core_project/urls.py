# core_project/urls.py
"""
Configuración de URLs principal del Sistema de Agendamiento.
Define las rutas base del proyecto.
"""
from django.contrib import admin
from django.urls import path, include
from agendamiento import views as agendamiento_views

urlpatterns = [
    path('admin/', admin.site.urls),  # Panel administrativo de Django
    path('agendamiento/', include('agendamiento.urls', namespace='agendamiento')),  # App principal
    path('', agendamiento_views.pagina_inicio, name='pagina_inicio'),  # Página de inicio
]