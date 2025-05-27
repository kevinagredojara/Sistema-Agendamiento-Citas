# agendamiento/views_profesional.py
from django.shortcuts import render, get_object_or_404, redirect 
# from django.http import HttpResponse # Ya no se usa para registrar_asistencia_cita
from django.urls import reverse 
from django.contrib.auth.decorators import login_required
from django.utils import timezone, formats 
from django.utils.translation import gettext_lazy as _
from django.contrib import messages 
from django.views.decorators.http import require_POST 

from .decorators import profesional_required 
from .models import Cita, ProfesionalSalud, Paciente # Aseguramos Paciente por si se usa directamente
from datetime import datetime, time, timedelta # timedelta y time podrían no ser necesarias aquí


@login_required
@profesional_required
def ver_agenda_profesional(request):
    try:
        profesional_actual = get_object_or_404(ProfesionalSalud, user_account=request.user)
    except ProfesionalSalud.DoesNotExist:
        profesional_actual = None 
        messages.error(request, "Perfil de profesional no encontrado.") 
        return redirect('agendamiento:login') 

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
        # Mostramos citas Programadas, Realizadas y No Asistió en la agenda para el día
        citas_del_dia = Cita.objects.filter(
            profesional=profesional_actual,
            fecha_hora_inicio_cita__date=fecha_agenda
        ).exclude(estado_cita='Cancelada').order_by('fecha_hora_inicio_cita').select_related('paciente__user_account')
    
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

@login_required
@profesional_required
def ver_detalles_paciente_cita(request, cita_id):
    cita_contexto = get_object_or_404(Cita.objects.select_related('paciente__user_account', 'profesional__user_account'), id=cita_id)
    paciente = cita_contexto.paciente
    
    try:
        profesional_actual = request.user.profesional_perfil
    except ProfesionalSalud.DoesNotExist: 
        messages.error(request, "No se pudo verificar su perfil de profesional.")
        return redirect('agendamiento:dashboard_profesional')

    if cita_contexto.profesional != profesional_actual:
        messages.error(request, "No tiene permiso para ver los detalles del paciente de esta cita.")
        return redirect('agendamiento:ver_agenda_profesional') 

    fecha_agenda_original_str = request.GET.get('fecha_agenda_original')
    fecha_agenda_original_obj = None
    if fecha_agenda_original_str:
        try:
            fecha_agenda_original_obj = datetime.strptime(fecha_agenda_original_str, '%Y-%m-%d').date()
        except ValueError:
            pass 
            
    context = {
        'titulo_pagina': f"Detalles del Paciente: {paciente.user_account.get_full_name()}",
        'cita_contexto': cita_contexto,
        'paciente': paciente,
        'fecha_agenda_original': fecha_agenda_original_obj 
    }
    return render(request, 'agendamiento/detalles_paciente_cita.html', context)

# VISTA ACTUALIZADA PARA REGISTRAR ASISTENCIA (HU-MED-004) 👇
@login_required
@profesional_required
@require_POST # Esta vista solo aceptará solicitudes POST
def registrar_asistencia_cita(request, cita_id):
    cita = get_object_or_404(Cita.objects.select_related('paciente__user_account', 'profesional'), id=cita_id)
    
    # Verificar que el profesional logueado sea el asignado a la cita
    try:
        profesional_actual = request.user.profesional_perfil
    except ProfesionalSalud.DoesNotExist:
        messages.error(request, "No se pudo verificar su perfil de profesional.")
        return redirect('agendamiento:dashboard_profesional')

    if cita.profesional != profesional_actual:
        messages.error(request, "No tiene permiso para registrar la asistencia de esta cita.")
        # Redirigir a la agenda del día de la cita para mantener contexto
        fecha_cita_str = cita.fecha_hora_inicio_cita.strftime('%Y-%m-%d')
        return redirect(f"{reverse('agendamiento:ver_agenda_profesional')}?fecha_agenda={fecha_cita_str}")

    # Solo permitir registrar asistencia para citas 'Programada'
    if cita.estado_cita != 'Programada':
        messages.warning(request, f"La asistencia para la cita de {cita.paciente.user_account.get_full_name()} el {formats.date_format(cita.fecha_hora_inicio_cita, 'd/m/Y H:i')} ya fue registrada o la cita fue cancelada (estado: '{cita.get_estado_cita_display()}').")
        fecha_cita_str = cita.fecha_hora_inicio_cita.strftime('%Y-%m-%d')
        return redirect(f"{reverse('agendamiento:ver_agenda_profesional')}?fecha_agenda={fecha_cita_str}")

    nuevo_estado = request.POST.get('nuevo_estado')

    if nuevo_estado not in ['Realizada', 'No_Asistio']:
        messages.error(request, "Acción de asistencia no válida.")
        fecha_cita_str = cita.fecha_hora_inicio_cita.strftime('%Y-%m-%d')
        return redirect(f"{reverse('agendamiento:ver_agenda_profesional')}?fecha_agenda={fecha_cita_str}")

    cita.estado_cita = nuevo_estado
    cita.save()

    estado_legible = "Asistió (Realizada)" if nuevo_estado == 'Realizada' else "No Asistió"
    messages.success(request, f"Se ha registrado la asistencia para {cita.paciente.user_account.get_full_name()} como: '{estado_legible}'.")
    
    # Redirigir a la agenda del día de la cita
    fecha_cita_str = cita.fecha_hora_inicio_cita.strftime('%Y-%m-%d')
    return redirect(f"{reverse('agendamiento:ver_agenda_profesional')}?fecha_agenda={fecha_cita_str}")