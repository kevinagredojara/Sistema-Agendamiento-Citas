"""Vistas para el rol de Paciente."""

from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone, formats
from django.utils.translation import gettext_lazy as _

from .decorators import paciente_required
from .forms import PacienteDatosContactoForm
from .models import Cita, Paciente

@login_required
@paciente_required
def ver_proximas_citas(request):
    """Muestra las próximas citas programadas del paciente."""
    try:
        paciente_actual = get_object_or_404(Paciente, user_account=request.user)
    except Paciente.DoesNotExist:
        paciente_actual = None
        messages.error(request, "Perfil de paciente no encontrado.")
        return redirect('agendamiento:dashboard_paciente')

    # Obtener citas futuras en estado 'Programada'
    proximas_citas = []
    if paciente_actual:
        ahora = timezone.now()
        proximas_citas = Cita.objects.filter(
            paciente=paciente_actual,
            fecha_hora_inicio_cita__gte=ahora,
            estado_cita='Programada'
        ).order_by('fecha_hora_inicio_cita').select_related(
            'profesional__user_account',
            'profesional__especialidad'
        )

    context = {
        'titulo_pagina': "Mis Próximas Citas",
        'proximas_citas': proximas_citas,
    }
    return render(request, 'agendamiento/mis_proximas_citas.html', context)

@login_required
@paciente_required
def ver_historial_citas(request):
    """Muestra el historial de citas pasadas, realizadas, canceladas o no asistidas."""
    try:
        paciente_actual = get_object_or_404(Paciente, user_account=request.user)
    except Paciente.DoesNotExist:
        messages.error(request, "Perfil de paciente no encontrado.")
        return redirect('agendamiento:dashboard_paciente')

    # Obtener citas pasadas o con estado final (Realizada, No_Asistio, Cancelada)
    ahora = timezone.now()
    historial_citas = Cita.objects.filter(
        Q(paciente=paciente_actual) &
        (Q(fecha_hora_inicio_cita__lt=ahora) |
         Q(estado_cita__in=['Realizada', 'No_Asistio', 'Cancelada']))
    ).order_by('-fecha_hora_inicio_cita').select_related(
        'profesional__user_account',
        'profesional__especialidad'
    )

    context = {
        'titulo_pagina': "Mi Historial de Citas",
        'historial_citas': historial_citas,
    }
    return render(request, 'agendamiento/mis_historial_citas.html', context)

@login_required
@paciente_required
def actualizar_datos_paciente(request):
    """Permite al paciente actualizar su email y teléfono de contacto."""
    paciente_actual = get_object_or_404(Paciente, user_account=request.user)
    user_actual = request.user
    form_message = None

    if request.method == 'POST':
        form = PacienteDatosContactoForm(request.POST, initial={
            'email': user_actual.email,
            'telefono_contacto': paciente_actual.telefono_contacto
        })
        if form.is_valid():
            new_email = form.cleaned_data['email']
            new_telefono = form.cleaned_data['telefono_contacto']

            email_changed = (new_email.lower() != user_actual.email.lower())
            telefono_changed = (new_telefono != paciente_actual.telefono_contacto)

            # Actualizar datos si hubo cambios
            if email_changed or telefono_changed:
                try:
                    if email_changed:
                        user_actual.email = new_email
                        user_actual.save(update_fields=['email'])

                    if telefono_changed:
                        paciente_actual.telefono_contacto = new_telefono
                        paciente_actual.save(update_fields=['telefono_contacto'])

                    return redirect('agendamiento:actualizacion_datos_exitosa_paciente')
                except Exception as e:
                    messages.error(request, f"Ocurrió un error al actualizar sus datos: {e}")
            else:
                form_message = "No se han realizado cambios en sus datos de contacto."
    else:
        form = PacienteDatosContactoForm(initial={
            'email': user_actual.email,
            'telefono_contacto': paciente_actual.telefono_contacto
        })

    context = {
        'form': form,
        'titulo_pagina': "Actualizar Mis Datos de Contacto",
        'form_message': form_message
    }
    return render(request, 'agendamiento/actualizar_datos_paciente_form.html', context)

@login_required
@paciente_required
def actualizacion_datos_exitosa(request):
    """Vista de confirmación después de actualizar los datos del paciente."""
    context = {
        'titulo_pagina': "Datos Actualizados Exitosamente"
    }
    return render(request, 'agendamiento/actualizacion_datos_exitosa_paciente.html', context)