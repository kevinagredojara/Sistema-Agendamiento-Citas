# agendamiento/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Importamos solo los decoradores necesarios para las vistas que quedan aquí
from .decorators import profesional_required, paciente_required 
# Ya no necesitamos importar User, messages, otros forms, otros modelos, etc., aquí
# a menos que pagina_inicio los necesite (que actualmente no lo hace).

@login_required
def pagina_inicio(request):
    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'agendamiento/inicio.html', context)

# El dashboard_asesor se ha movido a views_asesor.py

@login_required
@profesional_required
def dashboard_profesional(request):
    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'agendamiento/dashboard_profesional.html', context)

@login_required
@paciente_required
def dashboard_paciente(request):
    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'agendamiento/dashboard_paciente.html', context)

# Todas las demás vistas (registrar_paciente, listar_pacientes, actualizar_paciente,
# consultar_disponibilidad, seleccionar_paciente_para_cita, visualizar_citas_gestionadas,
# modificar_cita, confirmar_modificacion_cita) DEBEN SER ELIMINADAS DE ESTE ARCHIVO,
# ya que ahora residen en agendamiento/views_asesor.py