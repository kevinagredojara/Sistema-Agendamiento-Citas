# agendamiento/views_profesional.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone, formats
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.views.decorators.http import require_POST

from .decorators import profesional_required
from .models import Cita, ProfesionalSalud, Paciente
from datetime import datetime, time, timedelta

@login_required
@profesional_required
def ver_agenda_profesional(request):
    try:
        profesional_actual = get_object_or_404(ProfesionalSalud, user_account=request.user)
    except ProfesionalSalud.DoesNotExist:
        profesional_actual = None 
        messages.error(request, "Perfil de profesional no encontrado.") 
        return redirect('agendamiento:login') 

    # citas_del_dia_originales = [] # Cambiaremos cómo se maneja esto
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

    citas_para_plantilla = [] # Lista para los objetos de cita enriquecidos
    ahora = timezone.now() # Obtener la hora actual una vez

    if profesional_actual:
        citas_query = Cita.objects.filter(
            profesional=profesional_actual,
            fecha_hora_inicio_cita__date=fecha_agenda
        ).exclude(estado_cita='Cancelada').order_by('fecha_hora_inicio_cita').select_related('paciente__user_account')
        
        for cita in citas_query:
            # Añadimos el flag directamente al objeto cita para la plantilla
            # Esto es seguro si no guardamos el objeto cita después de esto en esta vista.
            # O podemos crear un diccionario/objeto wrapper si preferimos no mutar.
            # Por simplicidad aquí, añadimos un atributo.
            cita.puede_registrar_asistencia = ahora > cita.fecha_hora_fin_cita
            citas_para_plantilla.append(cita)
    
    de_str = _('de')
    dia_sem_str = formats.date_format(fecha_agenda, "l")
    dia_num_str = formats.date_format(fecha_agenda, "d")
    mes_str = formats.date_format(fecha_agenda, "F")
    anho_str = formats.date_format(fecha_agenda, "Y")
    fecha_agenda_formateada = f"{dia_sem_str}, {dia_num_str} {de_str} {mes_str} {de_str} {anho_str}"
    
    context = {
        'titulo_pagina': f"Mi Agenda - {fecha_agenda_formateada}",
        'profesional_actual': profesional_actual,
        'citas_del_dia': citas_para_plantilla, # Usamos la nueva lista
        'fecha_agenda': fecha_agenda, 
        'fecha_agenda_formateada': fecha_agenda_formateada 
    }
    return render(request, 'agendamiento/agenda_profesional.html', context)

@login_required
@profesional_required
def ver_detalles_paciente_cita(request, cita_id):
    cita_contexto = get_object_or_404(Cita.objects.select_related('paciente__user_account', 'profesional__user_account', 'profesional__especialidad'), id=cita_id)
    paciente = cita_contexto.paciente
    
    profesional_actual = get_object_or_404(ProfesionalSalud, user_account=request.user)

    if cita_contexto.profesional != profesional_actual:
        messages.error(request, "No tiene permiso para ver los detalles del paciente de esta cita.")
        fecha_agenda_original_str = request.GET.get('fecha_agenda_original')
        if fecha_agenda_original_str:
            return redirect(f"{reverse('agendamiento:ver_agenda_profesional')}?fecha_agenda={fecha_agenda_original_str}")
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

@login_required
@profesional_required
@require_POST 
def registrar_asistencia_cita(request, cita_id):
    cita = get_object_or_404(Cita.objects.select_related('paciente__user_account', 'profesional'), id=cita_id)
    profesional_actual = get_object_or_404(ProfesionalSalud, user_account=request.user)
    
    fecha_cita_para_redirect_str = cita.fecha_hora_inicio_cita.strftime('%Y-%m-%d')
    url_redirect_agenda = f"{reverse('agendamiento:ver_agenda_profesional')}?fecha_agenda={fecha_cita_para_redirect_str}"

    if cita.profesional != profesional_actual:
        messages.error(request, "No tiene permiso para registrar la asistencia de esta cita.")
        return redirect(url_redirect_agenda)

    if cita.estado_cita != 'Programada':
        de_str = _('de')
        dia_sem_str = formats.date_format(cita.fecha_hora_inicio_cita, "l")
        dia_num_str = formats.date_format(cita.fecha_hora_inicio_cita, "d")
        mes_str = formats.date_format(cita.fecha_hora_inicio_cita, "F")
        anho_str = formats.date_format(cita.fecha_hora_inicio_cita, "Y")
        hora_str = timezone.localtime(cita.fecha_hora_inicio_cita).strftime('%H:%M')
        fecha_cita_formateada = f"{dia_sem_str}, {dia_num_str} {de_str} {mes_str} {de_str} {anho_str} a las {hora_str}"
        messages.warning(request, f"La asistencia para la cita de {cita.paciente.user_account.get_full_name()} el {fecha_cita_formateada} ya fue registrada o la cita fue cancelada (estado: '{cita.get_estado_cita_display()}').")
        return redirect(url_redirect_agenda)

    ahora = timezone.now()
    if ahora <= cita.fecha_hora_fin_cita:
        hora_fin_cita_formateada = timezone.localtime(cita.fecha_hora_fin_cita).strftime('%H:%M')
        messages.info(request, f"Aún no puede registrar la asistencia para esta cita. Debe esperar hasta después de las {hora_fin_cita_formateada}.")
        return redirect(url_redirect_agenda)

    nuevo_estado = request.POST.get('nuevo_estado')

    if nuevo_estado not in ['Realizada', 'No_Asistio']:
        messages.error(request, "Acción de asistencia no válida.")
        return redirect(url_redirect_agenda)

    cita.estado_cita = nuevo_estado
    cita.save()

    estado_legible = _("Asistió (Realizada)") if nuevo_estado == 'Realizada' else _("No Asistió")
    messages.success(request, f"Se ha registrado la asistencia para {cita.paciente.user_account.get_full_name()} como: '{estado_legible}'.")
    
    return redirect(url_redirect_agenda)

@login_required
@profesional_required
def confirmar_asistencia_cita(request, cita_id):
    cita = get_object_or_404(Cita.objects.select_related('paciente__user_account', 'profesional__user_account', 'profesional__especialidad'), id=cita_id)
    estado_propuesto = request.GET.get('estado_propuesto')
    fecha_agenda_original_str = request.GET.get('fecha_agenda')

    profesional_actual = get_object_or_404(ProfesionalSalud, user_account=request.user)
    url_redirect_agenda_confirm = reverse('agendamiento:ver_agenda_profesional')
    if fecha_agenda_original_str:
        url_redirect_agenda_confirm += f"?fecha_agenda={fecha_agenda_original_str}"

    if cita.profesional != profesional_actual:
        messages.error(request, "No tiene permiso para confirmar la asistencia de esta cita.")
        return redirect(url_redirect_agenda_confirm)

    if estado_propuesto not in ['Realizada', 'No_Asistio']:
        messages.error(request, "Acción de asistencia propuesta no válida.")
        return redirect(url_redirect_agenda_confirm)
    
    if cita.estado_cita != 'Programada':
        de_str = _('de')
        # ... (formateo de fecha_cita_formateada como antes) ...
        dia_sem_str = formats.date_format(cita.fecha_hora_inicio_cita, "l")
        dia_num_str = formats.date_format(cita.fecha_hora_inicio_cita, "d")
        mes_str = formats.date_format(cita.fecha_hora_inicio_cita, "F")
        anho_str = formats.date_format(cita.fecha_hora_inicio_cita, "Y")
        hora_str = timezone.localtime(cita.fecha_hora_inicio_cita).strftime('%H:%M')
        fecha_cita_formateada = f"{dia_sem_str}, {dia_num_str} {de_str} {mes_str} {de_str} {anho_str} a las {hora_str}"
        messages.warning(request, f"La asistencia para la cita de {cita.paciente.user_account.get_full_name()} el {fecha_cita_formateada} ya fue registrada o la cita fue cancelada (estado actual: '{cita.get_estado_cita_display()}').")
        return redirect(url_redirect_agenda_confirm)

    ahora = timezone.now()
    if ahora <= cita.fecha_hora_fin_cita:
        hora_fin_cita_formateada = timezone.localtime(cita.fecha_hora_fin_cita).strftime('%H:%M')
        messages.info(request, f"Aún no puede registrar la asistencia para la cita de {cita.paciente.user_account.get_full_name()}. La cita finaliza a las {hora_fin_cita_formateada}.")
        return redirect(url_redirect_agenda_confirm)

    fecha_agenda_original_obj = None
    if fecha_agenda_original_str:
        try:
            fecha_agenda_original_obj = datetime.strptime(fecha_agenda_original_str, '%Y-%m-%d').date()
        except ValueError:
            pass 

    context = {
        'cita': cita, 
        'estado_propuesto': estado_propuesto,
        'fecha_agenda_original': fecha_agenda_original_obj,
        'titulo_pagina': f"Confirmar Asistencia para Cita"
    }
    return render(request, 'agendamiento/confirmar_asistencia_cita_template.html', context)