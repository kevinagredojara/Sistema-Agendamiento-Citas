# agendamiento/views_profesional.py
from django.shortcuts import render, get_object_or_404, redirect # redirect añadido
# from django.http import HttpResponse # Ya no se usa para ver_detalles_paciente_cita
from django.contrib.auth.decorators import login_required
from django.utils import timezone, formats 
from django.utils.translation import gettext_lazy as _
from django.contrib import messages # messages añadido

from .decorators import profesional_required 
from .models import Cita, ProfesionalSalud, Paciente # Paciente añadido
from datetime import datetime # datetime añadido


@login_required
@profesional_required
def ver_agenda_profesional(request):
    try:
        profesional_actual = get_object_or_404(ProfesionalSalud, user_account=request.user)
    except ProfesionalSalud.DoesNotExist:
        profesional_actual = None 
        messages.error(request, "Perfil de profesional no encontrado.") # Mensaje de error
        return redirect('agendamiento:login') # O alguna otra página segura

    citas_del_dia = []
    fecha_agenda_str = request.GET.get('fecha_agenda', None)
    fecha_agenda = None

    if fecha_agenda_str:
        try:
            fecha_agenda = datetime.strptime(fecha_agenda_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de fecha inválido. Mostrando agenda de hoy.")
            fecha_agenda = timezone.localdate() 
    else:
        fecha_agenda = timezone.localdate() 

    if profesional_actual:
        citas_del_dia = Cita.objects.filter(
            profesional=profesional_actual,
            fecha_hora_inicio_cita__date=fecha_agenda, 
            estado_cita='Programada' 
        ).order_by('fecha_hora_inicio_cita').select_related('paciente__user_account')
    
    de_str = _('de')
    dia_sem_str = formats.date_format(fecha_agenda, "l")
    dia_num_str = formats.date_format(fecha_agenda, "d")
    mes_str = formats.date_format(fecha_agenda, "F")
    anho_str = formats.date_format(fecha_agenda, "Y")
    fecha_agenda_formateada = f"{dia_sem_str}, {dia_num_str} {de_str} {mes_str} {de_str} {anho_str}"
    
    context = {
        'titulo_pagina': f"Mi Agenda - {fecha_agenda_formateada}",
        'profesional_actual': profesional_actual,
        'citas_del_dia': citas_del_dia,
        'fecha_agenda': fecha_agenda, 
        'fecha_agenda_formateada': fecha_agenda_formateada 
    }
    return render(request, 'agendamiento/agenda_profesional.html', context)

# VISTA ACTUALIZADA PARA VER DETALLES DEL PACIENTE DE UNA CITA (HU-MED-005) 👇
@login_required
@profesional_required
def ver_detalles_paciente_cita(request, cita_id):
    cita_contexto = get_object_or_404(Cita.objects.select_related('paciente__user_account', 'profesional__user_account'), id=cita_id)
    paciente = cita_contexto.paciente
    
    # Verificar que el profesional logueado sea el asignado a la cita
    try:
        profesional_actual = request.user.profesional_perfil
    except ProfesionalSalud.DoesNotExist: # O la forma que uses para obtener el perfil
        messages.error(request, "No se pudo verificar su perfil de profesional.")
        return redirect('agendamiento:dashboard_profesional') # O a donde sea apropiado

    if cita_contexto.profesional != profesional_actual:
        messages.error(request, "No tiene permiso para ver los detalles del paciente de esta cita.")
        return redirect('agendamiento:ver_agenda_profesional') 

    # Obtener la fecha_agenda_original de los parámetros GET para el botón "Volver"
    fecha_agenda_original_str = request.GET.get('fecha_agenda_original')
    fecha_agenda_original_obj = None
    if fecha_agenda_original_str:
        try:
            fecha_agenda_original_obj = datetime.strptime(fecha_agenda_original_str, '%Y-%m-%d').date()
        except ValueError:
            # No hacer nada o loggear, el botón "Volver" simplemente no tendrá la fecha
            pass 
            
    context = {
        'titulo_pagina': f"Detalles del Paciente: {paciente.user_account.get_full_name()}",
        'cita_contexto': cita_contexto,
        'paciente': paciente,
        'fecha_agenda_original': fecha_agenda_original_obj # Para el enlace "Volver a Mi Agenda"
    }
    return render(request, 'agendamiento/detalles_paciente_cita.html', context)

# Aquí irán las otras vistas del profesional:
# - registrar_asistencia_cita (HU-MED-004)