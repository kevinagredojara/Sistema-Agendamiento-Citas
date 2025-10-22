"""Vistas generales y dashboards principales de la aplicación."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .decorators import profesional_required, paciente_required

@login_required
def pagina_inicio(request):
    """Página de inicio para usuarios autenticados."""
    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'agendamiento/inicio.html', context)

@login_required
@profesional_required
def dashboard_profesional(request):
    """Dashboard principal para el rol de Profesional de Salud."""
    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'agendamiento/dashboard_profesional.html', context)

@login_required
@paciente_required
def dashboard_paciente(request):
    """Dashboard principal para el rol de Paciente."""
    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'agendamiento/dashboard_paciente.html', context)
