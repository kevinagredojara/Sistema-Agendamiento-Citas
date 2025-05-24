# agendamiento/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# IMPORTAMOS TODOS LOS DECORADORES NECESARIOS
from .decorators import asesor_required, profesional_required, paciente_required

@login_required
def pagina_inicio(request):
    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'agendamiento/inicio.html', context)

@login_required
@asesor_required
def dashboard_asesor(request):
    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'agendamiento/dashboard_asesor.html', context)

@login_required
@profesional_required
def dashboard_profesional(request):
    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
        # Más adelante podríamos pasar la agenda del profesional aquí
    }
    return render(request, 'agendamiento/dashboard_profesional.html', context)

# NUEVA VISTA PARA EL DASHBOARD DEL PACIENTE
@login_required
@paciente_required # Usamos el decorador para pacientes
def dashboard_paciente(request):
    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
        # Más adelante podríamos pasar las citas del paciente aquí
    }
    return render(request, 'agendamiento/dashboard_paciente.html', context)