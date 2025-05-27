# agendamiento/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse 
from django.urls import reverse # IMPORTACIÓN AÑADIDA AQUÍ 👇
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .decorators import asesor_required, profesional_required, paciente_required
from .forms import (
    UserForm, PacienteForm, UserUpdateForm, 
    ConsultaDisponibilidadForm, BuscarPacientePorDocumentoForm, CitaFilterForm,
    ModificarCitaForm 
)
from .models import Paciente, ProfesionalSalud, PlantillaHorarioMedico, Cita 
from datetime import datetime, time, timedelta 
from django.core.mail import send_mail 
from django.conf import settings
from django.utils import timezone, formats 
from django.db.models import Q

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
    }
    return render(request, 'agendamiento/dashboard_profesional.html', context)

@login_required
@paciente_required
def dashboard_paciente(request):
    context = {
        'nombre_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'agendamiento/dashboard_paciente.html', context)

@login_required
@asesor_required
def registrar_paciente(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, prefix='user')
        paciente_form = PacienteForm(request.POST, prefix='paciente')
        if user_form.is_valid() and paciente_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.first_name = user_form.cleaned_data.get('first_name', '')
            new_user.last_name = user_form.cleaned_data.get('last_name', '')
            new_user.email = user_form.cleaned_data.get('email', '')
            new_user.save()
            new_paciente = paciente_form.save(commit=False)
            new_paciente.user_account = new_user
            new_paciente.save()
            messages.success(request, f'¡Paciente {new_user.first_name} {new_user.last_name} registrado exitosamente!')
            return redirect('agendamiento:dashboard_asesor')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        user_form = UserForm(prefix='user')
        paciente_form = PacienteForm(prefix='paciente')
    context = {
        'user_form': user_form, 'paciente_form': paciente_form,
        'titulo_pagina': 'Registrar Nuevo Paciente'
    }
    return render(request, 'agendamiento/registrar_paciente_form.html', context)

@login_required
@asesor_required
def listar_pacientes(request):
    pacientes = Paciente.objects.all().order_by('user_account__last_name', 'user_account__first_name')
    context = {'pacientes': pacientes, 'titulo_pagina': 'Listado de Pacientes'}
    return render(request, 'agendamiento/listar_pacientes.html', context)

@login_required
@asesor_required
def actualizar_paciente(request, paciente_id):
    paciente_a_actualizar = get_object_or_404(Paciente, id=paciente_id)
    usuario_a_actualizar = paciente_a_actualizar.user_account
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=usuario_a_actualizar, prefix='user')
        paciente_form = PacienteForm(request.POST, instance=paciente_a_actualizar, prefix='paciente')
        if user_form.is_valid() and paciente_form.is_valid():
            user_form.save()
            paciente_form.save()
            messages.success(request, f'¡Datos del paciente {usuario_a_actualizar.get_full_name() or usuario_a_actualizar.username} actualizados exitosamente!')
            return redirect('agendamiento:listar_pacientes')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        user_form = UserUpdateForm(instance=usuario_a_actualizar, prefix='user')
        paciente_form = PacienteForm(instance=paciente_a_actualizar, prefix='paciente')
    context = {
        'user_form': user_form, 'paciente_form': paciente_form,
        'paciente_a_actualizar': paciente_a_actualizar,
        'titulo_pagina': f'Actualizar Paciente: {usuario_a_actualizar.get_full_name() or usuario_a_actualizar.username}'
    }
    return render(request, 'agendamiento/actualizar_paciente_form.html', context)

@login_required
@asesor_required
def consultar_disponibilidad(request):
    form = ConsultaDisponibilidadForm(request.GET or None)
    slots_disponibles = []
    profesional_seleccionado = None
    fecha_seleccionada = None
    if form.is_valid():
        profesional_seleccionado = form.cleaned_data['profesional']
        fecha_seleccionada = form.cleaned_data['fecha']
        if profesional_seleccionado and fecha_seleccionada:
            dia_semana_seleccionado = fecha_seleccionada.weekday()
            plantillas = PlantillaHorarioMedico.objects.filter(
                profesional=profesional_seleccionado,
                dia_semana=dia_semana_seleccionado
            ).order_by('hora_inicio_bloque')
            current_tz = timezone.get_current_timezone() 
            inicio_del_dia_seleccionado = timezone.make_aware(datetime.combine(fecha_seleccionada, time.min), current_tz)
            fin_del_dia_seleccionado = timezone.make_aware(datetime.combine(fecha_seleccionada, time.max), current_tz)
            citas_ocupadas_qs = Cita.objects.filter(
                profesional=profesional_seleccionado,
                fecha_hora_inicio_cita__gte=inicio_del_dia_seleccionado,
                fecha_hora_inicio_cita__lte=fin_del_dia_seleccionado,
                estado_cita='Programada'
            )
            rangos_ocupados = []
            for cita_ocupada in citas_ocupadas_qs:
                hora_inicio_local_ocupada = timezone.localtime(cita_ocupada.fecha_hora_inicio_cita, current_tz).time()
                hora_fin_local_ocupada = timezone.localtime(cita_ocupada.fecha_hora_fin_cita, current_tz).time()
                rangos_ocupados.append((hora_inicio_local_ocupada, hora_fin_local_ocupada))
            duracion_consulta = profesional_seleccionado.especialidad.duracion_consulta_minutos
            for plantilla in plantillas:
                hora_inicio_iteracion_naive = datetime.combine(fecha_seleccionada, plantilla.hora_inicio_bloque)
                hora_fin_iteracion_bloque_naive = datetime.combine(fecha_seleccionada, plantilla.hora_fin_bloque)
                hora_inicio_iteracion = timezone.make_aware(hora_inicio_iteracion_naive, current_tz)
                hora_fin_iteracion_bloque = timezone.make_aware(hora_fin_iteracion_bloque_naive, current_tz)
                while hora_inicio_iteracion < hora_fin_iteracion_bloque:
                    hora_fin_slot_propuesto = hora_inicio_iteracion + timedelta(minutes=duracion_consulta)
                    if hora_fin_slot_propuesto > hora_fin_iteracion_bloque:
                        break 
                    slot_esta_ocupado = False
                    slot_inicio_time_local = hora_inicio_iteracion.astimezone(current_tz).time()
                    slot_fin_time_local = hora_fin_slot_propuesto.astimezone(current_tz).time()
                    for inicio_ocupado_local, fin_ocupado_local in rangos_ocupados:
                        if (slot_inicio_time_local < fin_ocupado_local and slot_fin_time_local > inicio_ocupado_local):
                            slot_esta_ocupado = True
                            break 
                    if not slot_esta_ocupado:
                        slots_disponibles.append((slot_inicio_time_local, slot_fin_time_local))
                    hora_inicio_iteracion = hora_fin_slot_propuesto
            if not slots_disponibles and plantillas.exists():
                 messages.info(request, f"No hay horarios disponibles para {profesional_seleccionado} el {fecha_seleccionada.strftime('%d/%m/%Y')}.")
            elif not plantillas.exists() and profesional_seleccionado and fecha_seleccionada:
                 fecha_formateada_advertencia = formats.date_format(fecha_seleccionada, "l, d/m/Y")
                 messages.warning(request, f"{profesional_seleccionado} no tiene un horario configurado para el día seleccionado ({fecha_formateada_advertencia}).")
    context = {
        'form': form, 'titulo_pagina': 'Consultar Disponibilidad de Citas',
        'slots_disponibles': slots_disponibles,
        'profesional_seleccionado': profesional_seleccionado,
        'fecha_seleccionada': fecha_seleccionada
    }
    return render(request, 'agendamiento/consultar_disponibilidad_form.html', context)

@login_required
@asesor_required
def seleccionar_paciente_para_cita(request, profesional_id, fecha_seleccionada_str, hora_inicio_slot_str):
    profesional = get_object_or_404(ProfesionalSalud, id=profesional_id)
    try:
        fecha_obj = datetime.strptime(fecha_seleccionada_str, '%Y-%m-%d').date()
        hora_obj = datetime.strptime(hora_inicio_slot_str, '%H:%M').time()
    except ValueError:
        messages.error(request, "Formato de fecha u hora inválido en la URL.")
        return redirect('agendamiento:consultar_disponibilidad')

    fecha_hora_inicio_cita_naive = datetime.combine(fecha_obj, hora_obj)
    current_tz = timezone.get_current_timezone()
    fecha_hora_inicio_cita_aware = timezone.make_aware(fecha_hora_inicio_cita_naive, current_tz)
    duracion_consulta = profesional.especialidad.duracion_consulta_minutos
    fecha_hora_fin_cita_aware = fecha_hora_inicio_cita_aware + timedelta(minutes=duracion_consulta)
    paciente_encontrado = None 
    form_buscar_paciente = BuscarPacientePorDocumentoForm(request.GET or None)
    if form_buscar_paciente.is_valid():
        numero_documento = form_buscar_paciente.cleaned_data['numero_documento']
        try:
            paciente_encontrado = Paciente.objects.get(numero_documento=numero_documento, user_account__is_active=True)
            messages.success(request, f"Paciente encontrado: {paciente_encontrado.user_account.get_full_name()}")
        except Paciente.DoesNotExist:
            messages.error(request, f"No se encontró un paciente activo con el número de documento '{numero_documento}'. Puede registrarlo si es necesario.")

    if request.method == 'POST':
        paciente_id_confirmado = request.POST.get('paciente_id_confirmado')
        if not paciente_id_confirmado:
            messages.error(request, "No se seleccionó un paciente para agendar la cita.")
        else:
            try:
                paciente_seleccionado = Paciente.objects.get(id=paciente_id_confirmado)
                if Cita.objects.filter(profesional=profesional, fecha_hora_inicio_cita=fecha_hora_inicio_cita_aware, estado_cita='Programada').exists():
                    messages.error(request, f"El horario de {hora_inicio_slot_str} para {profesional} el {fecha_obj.strftime('%d/%m/%Y')} ya no está disponible. Intente con otro.")
                else:
                    asesor_que_agenda_obj = None
                    if hasattr(request.user, 'asesor_perfil'):
                        asesor_que_agenda_obj = request.user.asesor_perfil
                    Cita.objects.create(
                        paciente=paciente_seleccionado,
                        profesional=profesional,
                        asesor_que_agenda=asesor_que_agenda_obj, 
                        fecha_hora_inicio_cita=fecha_hora_inicio_cita_aware,
                        fecha_hora_fin_cita=fecha_hora_fin_cita_aware,
                        estado_cita='Programada'
                    )
                    if paciente_seleccionado.user_account.email:
                        asunto = f"Confirmación de Cita Médica - {profesional.especialidad.nombre_especialidad}"
                        fecha_formateada_email = formats.date_format(fecha_obj, "l, d \d\e F \d\e Y") 
                        hora_formateada_email = time.strftime(hora_obj, '%I:%M %p').lower() 
                        
                        mensaje_email = (
                            f"Estimado(a) {paciente_seleccionado.user_account.get_full_name()},\n\n"
                            f"Le confirmamos su cita médica para el servicio de {profesional.especialidad.nombre_especialidad} "
                            f"con el/la Dr(a). {profesional.user_account.get_full_name()}.\n\n"
                            f"Fecha: {fecha_formateada_email}\n" 
                            f"Hora: {hora_formateada_email}\n\n" 
                            f"Por favor, llegue con anticipación.\n\n"
                            f"Saludos cordiales,\nIPS Medical Integral"
                        )
                        try:
                            send_mail(asunto, mensaje_email, settings.DEFAULT_FROM_EMAIL, [paciente_seleccionado.user_account.email], fail_silently=False)
                            messages.success(request, f"Cita agendada para {paciente_seleccionado.user_account.get_full_name()} con {profesional.user_account.get_full_name()} el {fecha_obj.strftime('%d/%m/%Y')} a las {hora_obj.strftime('%H:%M')}. Se envió correo de confirmación.")
                        except Exception as e:
                            messages.warning(request, f"Cita agendada para {paciente_seleccionado.user_account.get_full_name()} con {profesional.user_account.get_full_name()} el {fecha_obj.strftime('%d/%m/%Y')} a las {hora_obj.strftime('%H:%M')}. Hubo un problema al enviar el correo de confirmación: {e}")
                    else:
                        messages.success(request, f"Cita agendada para {paciente_seleccionado.user_account.get_full_name()} con {profesional.user_account.get_full_name()} el {fecha_obj.strftime('%d/%m/%Y')} a las {hora_obj.strftime('%H:%M')}. (Paciente sin email para notificación).")
                    return redirect('agendamiento:dashboard_asesor')
            except Paciente.DoesNotExist:
                messages.error(request, "El paciente seleccionado para agendar la cita no es válido.")
            except Exception as e: 
                messages.error(request, f"Error al crear la cita: {e}")
    context = {
        'profesional': profesional, 
        'fecha_seleccionada_obj': fecha_obj,
        'hora_inicio_slot_obj': hora_obj, 
        'fecha_hora_fin_cita': fecha_hora_fin_cita_aware,
        'titulo_pagina': 'Agendar Cita para Paciente',
        'form_buscar_paciente': form_buscar_paciente, 
        'paciente_encontrado': paciente_encontrado, 
        'profesional_id': profesional_id,
        'fecha_seleccionada_str': fecha_seleccionada_str,
        'hora_inicio_slot_str': hora_inicio_slot_str,
    }
    return render(request, 'agendamiento/seleccionar_paciente_para_cita.html', context)

@login_required
@asesor_required
def visualizar_citas_gestionadas(request):
    lista_citas = Cita.objects.select_related(
        'paciente__user_account', 
        'profesional__user_account', 
        'profesional__especialidad',
        'asesor_que_agenda__user_account'
    ).all()
    filter_form = CitaFilterForm(request.GET or None)
    if filter_form.is_valid():
        fecha_desde = filter_form.cleaned_data.get('fecha_desde')
        fecha_hasta = filter_form.cleaned_data.get('fecha_hasta')
        profesional_filtrado = filter_form.cleaned_data.get('profesional')
        estado_filtrado = filter_form.cleaned_data.get('estado_cita')
        if fecha_desde:
            fecha_desde_dt = timezone.make_aware(datetime.combine(fecha_desde, time.min), timezone.get_current_timezone())
            lista_citas = lista_citas.filter(fecha_hora_inicio_cita__gte=fecha_desde_dt)
        if fecha_hasta:
            fecha_hasta_dt = timezone.make_aware(datetime.combine(fecha_hasta, time.max), timezone.get_current_timezone())
            lista_citas = lista_citas.filter(fecha_hora_inicio_cita__lte=fecha_hasta_dt)
        if profesional_filtrado:
            lista_citas = lista_citas.filter(profesional=profesional_filtrado)
        if estado_filtrado: 
            lista_citas = lista_citas.filter(estado_cita=estado_filtrado)
    lista_citas = lista_citas.order_by('-fecha_hora_inicio_cita') 
    context = {
        'citas': lista_citas,
        'titulo_pagina': 'Citas Médicas Gestionadas',
        'filter_form': filter_form 
    }
    return render(request, 'agendamiento/visualizar_citas_gestionadas.html', context)

@login_required
@asesor_required
def modificar_cita(request, cita_id):
    cita_actual = get_object_or_404(Cita, id=cita_id)
    
    if cita_actual.estado_cita != 'Programada':
        messages.error(request, f"La cita (ID: {cita_actual.id}) no está 'Programada' y no puede ser modificada.")
        return redirect('agendamiento:visualizar_citas_gestionadas')

    slots_disponibles = []
    profesional_seleccionado_para_slots = None
    fecha_seleccionada_para_slots = None
    form = None 

    if request.method == 'POST': 
        profesional_final_id = request.POST.get('profesional_final_id')
        fecha_final_str = request.POST.get('fecha_final_str')
        hora_inicio_slot_seleccionada_str = request.POST.get('hora_inicio_slot_seleccionada')

        if not all([profesional_final_id, fecha_final_str, hora_inicio_slot_seleccionada_str]):
            messages.error(request, "Información incompleta para modificar la cita. Por favor, intente el proceso de nuevo desde la selección de horario.")
            return redirect('agendamiento:modificar_cita', cita_id=cita_actual.id)


        try:
            profesional_nuevo = get_object_or_404(ProfesionalSalud, id=profesional_final_id)
            if profesional_nuevo.especialidad != cita_actual.profesional.especialidad:
                 messages.error(request, "Error de consistencia: El profesional seleccionado no es de la especialidad original de la cita.")
                 return redirect('agendamiento:modificar_cita', cita_id=cita_actual.id)
            fecha_nueva_obj = datetime.strptime(fecha_final_str, '%Y-%m-%d').date()
            hora_nueva_obj = datetime.strptime(hora_inicio_slot_seleccionada_str, '%H:%M').time()
        except (ValueError):
            messages.error(request, "Datos inválidos (profesional, fecha u hora) para la nueva cita. Intente de nuevo.")
            return redirect('agendamiento:modificar_cita', cita_id=cita_actual.id)

        current_tz = timezone.get_current_timezone()
        nueva_fecha_hora_inicio = timezone.make_aware(datetime.combine(fecha_nueva_obj, hora_nueva_obj), current_tz)
        
        if profesional_nuevo.id == cita_actual.profesional_id and nueva_fecha_hora_inicio == cita_actual.fecha_hora_inicio_cita:
            messages.info(request, "No se han realizado cambios en los detalles de la cita, ya que los nuevos datos son idénticos a los actuales.")
            return redirect('agendamiento:visualizar_citas_gestionadas')

        nueva_fecha_hora_fin = nueva_fecha_hora_inicio + timedelta(minutes=profesional_nuevo.especialidad.duracion_consulta_minutos)
        citas_conflictivas = Cita.objects.filter(
            profesional=profesional_nuevo,
            fecha_hora_inicio_cita__lt=nueva_fecha_hora_fin,
            fecha_hora_fin_cita__gt=nueva_fecha_hora_inicio,
            estado_cita='Programada'
        ).exclude(id=cita_actual.id)

        if citas_conflictivas.exists():
            messages.error(request, f"El horario seleccionado ({hora_inicio_slot_seleccionada_str}) para {profesional_nuevo} el {formats.date_format(fecha_nueva_obj, 'd/m/Y')} ya no está disponible. Por favor, elija otro.")
            get_params_originales = request.session.get('modificar_cita_get_params', {})
            if get_params_originales:
                # Construir la query string para redirigir con los parámetros GET originales
                # Esto permite que el formulario de profesional/fecha se repueble como estaba
                # y el usuario pueda ver slots actualizados para esa selección.
                # Nota: reverse() necesita estar importado: from django.urls import reverse
                query_string = '&'.join([f'{k}={v}' for k,v in get_params_originales.items()])
                redirect_url = f"{reverse('agendamiento:modificar_cita', args=[cita_actual.id])}?{query_string}"
                return redirect(redirect_url)
            return redirect('agendamiento:modificar_cita', cita_id=cita_actual.id)
        
        cita_actual.profesional = profesional_nuevo
        cita_actual.fecha_hora_inicio_cita = nueva_fecha_hora_inicio
        cita_actual.fecha_hora_fin_cita = nueva_fecha_hora_fin
        cita_actual.save()

        paciente_nombre_completo = cita_actual.paciente.user_account.get_full_name()
        profesional_nuevo_nombre_completo = profesional_nuevo.user_account.get_full_name()
        especialidad_nombre = profesional_nuevo.especialidad.nombre_especialidad
        fecha_formateada_msg = formats.date_format(nueva_fecha_hora_inicio.date(), "l, d \d\e F \d\e Y")
        hora_formateada_msg = timezone.localtime(nueva_fecha_hora_inicio).strftime('%H:%M')

        mensaje_exito = (
            f"Cita ID {cita_actual.id} para {paciente_nombre_completo} modificada exitosamente. "
            f"Nueva cita con: {profesional_nuevo_nombre_completo} ({especialidad_nombre}) "
            f"el {fecha_formateada_msg} a las {hora_formateada_msg}."
        )

        if cita_actual.paciente.user_account.email:
            asunto = f"Actualización de su Cita Médica - {especialidad_nombre}"
            hora_formateada_email = timezone.localtime(nueva_fecha_hora_inicio).strftime('%I:%M %p').lower()
            mensaje_email = (
                f"Estimado(a) {paciente_nombre_completo},\n\n"
                f"Le informamos que su cita médica ha sido modificada.\n\n"
                f"Nuevos Detalles:\n"
                f"  - Profesional: {profesional_nuevo_nombre_completo}\n"
                f"  - Especialidad: {especialidad_nombre}\n"
                f"  - Fecha: {fecha_formateada_msg}\n" 
                f"  - Hora: {hora_formateada_email}\n\n"
                f"Saludos cordiales,\nIPS Medical Integral"
            )
            try:
                send_mail(asunto, mensaje_email, settings.DEFAULT_FROM_EMAIL, [cita_actual.paciente.user_account.email], fail_silently=False)
                messages.success(request, f"{mensaje_exito} Se envió correo de notificación.")
            except Exception as e:
                messages.warning(request, f"{mensaje_exito} Hubo un problema al enviar el correo de notificación: {e}")
        else:
            messages.success(request, f"{mensaje_exito} (Paciente sin email para notificación).")
        
        if 'modificar_cita_get_params' in request.session:
            del request.session['modificar_cita_get_params']
        return redirect('agendamiento:visualizar_citas_gestionadas')

    elif 'profesional' in request.GET and 'fecha_cita' in request.GET:
        form = ModificarCitaForm(request.GET, cita_actual=cita_actual)
        request.session['modificar_cita_get_params'] = request.GET.copy()
        if form.is_valid():
            profesional_nuevo = form.cleaned_data['profesional']
            fecha_nueva = form.cleaned_data['fecha_cita']
            profesional_seleccionado_para_slots = profesional_nuevo
            fecha_seleccionada_para_slots = fecha_nueva
            dia_semana_seleccionado = fecha_nueva.weekday()
            plantillas = PlantillaHorarioMedico.objects.filter(
                profesional=profesional_nuevo,
                dia_semana=dia_semana_seleccionado
            ).order_by('hora_inicio_bloque')
            current_tz = timezone.get_current_timezone()
            inicio_del_dia_seleccionado = timezone.make_aware(datetime.combine(fecha_nueva, time.min), current_tz)
            fin_del_dia_seleccionado = timezone.make_aware(datetime.combine(fecha_nueva, time.max), current_tz)
            citas_ocupadas_qs = Cita.objects.filter(
                profesional=profesional_nuevo,
                fecha_hora_inicio_cita__gte=inicio_del_dia_seleccionado,
                fecha_hora_inicio_cita__lte=fin_del_dia_seleccionado,
                estado_cita='Programada'
            ).exclude(id=cita_actual.id)
            rangos_ocupados = []
            for cita_ocupada in citas_ocupadas_qs:
                hora_inicio_local_ocupada = timezone.localtime(cita_ocupada.fecha_hora_inicio_cita, current_tz).time()
                hora_fin_local_ocupada = timezone.localtime(cita_ocupada.fecha_hora_fin_cita, current_tz).time()
                rangos_ocupados.append((hora_inicio_local_ocupada, hora_fin_local_ocupada))
            duracion_consulta = profesional_nuevo.especialidad.duracion_consulta_minutos
            for plantilla in plantillas:
                hora_inicio_iteracion_naive = datetime.combine(fecha_nueva, plantilla.hora_inicio_bloque)
                hora_fin_iteracion_bloque_naive = datetime.combine(fecha_nueva, plantilla.hora_fin_bloque)
                hora_inicio_iteracion = timezone.make_aware(hora_inicio_iteracion_naive, current_tz)
                hora_fin_iteracion_bloque = timezone.make_aware(hora_fin_iteracion_bloque_naive, current_tz)
                while hora_inicio_iteracion < hora_fin_iteracion_bloque:
                    hora_fin_slot_propuesto = hora_inicio_iteracion + timedelta(minutes=duracion_consulta)
                    if hora_fin_slot_propuesto > hora_fin_iteracion_bloque:
                        break 
                    slot_esta_ocupado = False
                    slot_inicio_time_local = hora_inicio_iteracion.astimezone(current_tz).time()
                    slot_fin_time_local = hora_fin_slot_propuesto.astimezone(current_tz).time()
                    for inicio_ocupado_local, fin_ocupado_local in rangos_ocupados:
                        if (slot_inicio_time_local < fin_ocupado_local and slot_fin_time_local > inicio_ocupado_local):
                            slot_esta_ocupado = True
                            break 
                    if not slot_esta_ocupado:
                        slots_disponibles.append((slot_inicio_time_local, slot_fin_time_local))
                    hora_inicio_iteracion = hora_fin_slot_propuesto
            if not slots_disponibles and plantillas.exists():
                 fecha_formateada_advertencia_mod = formats.date_format(fecha_nueva, "l, d/m/Y")
                 messages.info(request, f"No hay horarios disponibles para {profesional_nuevo} el {fecha_formateada_advertencia_mod}.")
            elif not plantillas.exists():
                 fecha_formateada_advertencia_mod_2 = formats.date_format(fecha_nueva, "l, d/m/Y")
                 messages.warning(request, f"{profesional_nuevo} no tiene un horario configurado para el día seleccionado ({fecha_formateada_advertencia_mod_2}).")
    else: 
        initial_data = {
            'profesional': cita_actual.profesional,
            'fecha_cita': cita_actual.fecha_hora_inicio_cita.astimezone(timezone.get_current_timezone()).date()
        }
        form = ModificarCitaForm(initial=initial_data, cita_actual=cita_actual)
        profesional_seleccionado_para_slots = cita_actual.profesional 
        fecha_seleccionada_para_slots = initial_data['fecha_cita']
        if 'modificar_cita_get_params' in request.session:
            del request.session['modificar_cita_get_params']

    context = {
        'cita_actual': cita_actual,
        'form': form,
        'slots_disponibles': slots_disponibles,
        'profesional_seleccionado_para_slots': profesional_seleccionado_para_slots,
        'fecha_seleccionada_para_slots': fecha_seleccionada_para_slots,
        'titulo_pagina': f'Modificar Cita ID: {cita_actual.id}'
    }
    return render(request, 'agendamiento/modificar_cita_form.html', context)

@login_required
@asesor_required
def confirmar_modificacion_cita(request, cita_id):
    cita_actual = get_object_or_404(Cita, id=cita_id)

    if cita_actual.estado_cita != 'Programada':
        messages.error(request, f"La cita (ID: {cita_actual.id}) que intenta confirmar no está 'Programada'. La modificación no puede continuar.")
        return redirect('agendamiento:visualizar_citas_gestionadas')

    profesional_propuesto_id = request.GET.get('profesional_id')
    fecha_propuesta_str = request.GET.get('fecha_cita') 
    hora_propuesta_str = request.GET.get('hora_cita')  

    if not all([profesional_propuesto_id, fecha_propuesta_str, hora_propuesta_str]):
        messages.error(request, "Faltan datos para confirmar la modificación (profesional, fecha o hora). Por favor, intente el proceso de modificación nuevamente.")
        return redirect('agendamiento:modificar_cita', cita_id=cita_id)

    try:
        profesional_propuesto = get_object_or_404(ProfesionalSalud, id=profesional_propuesto_id)
        if profesional_propuesto.especialidad != cita_actual.profesional.especialidad:
            messages.error(request, "Error de consistencia: El profesional propuesto no pertenece a la especialidad original de la cita.")
            return redirect('agendamiento:modificar_cita', cita_id=cita_id)
            
        fecha_propuesta = datetime.strptime(fecha_propuesta_str, '%Y-%m-%d').date()
        hora_propuesta = datetime.strptime(hora_propuesta_str, '%H:%M').time()
    except (ValueError, ProfesionalSalud.DoesNotExist):
        messages.error(request, "Datos del profesional, fecha u hora propuestos son inválidos. Por favor, intente el proceso de modificación nuevamente.")
        return redirect('agendamiento:modificar_cita', cita_id=cita_id)

    current_tz = timezone.get_current_timezone()
    propuesta_fecha_hora_inicio = timezone.make_aware(datetime.combine(fecha_propuesta, hora_propuesta), current_tz)

    if profesional_propuesto.id == cita_actual.profesional_id and propuesta_fecha_hora_inicio == cita_actual.fecha_hora_inicio_cita:
        messages.info(request, "La modificación propuesta es idéntica a la cita actual. No se requieren cambios.")
        return redirect('agendamiento:visualizar_citas_gestionadas')

    context = {
        'cita_actual': cita_actual,
        'profesional_propuesto': profesional_propuesto,
        'fecha_propuesta': fecha_propuesta,
        'hora_propuesta': hora_propuesta,
        'titulo_pagina': f"Confirmar Modificación Cita ID: {cita_actual.id}"
    }
    return render(request, 'agendamiento/confirmar_modificacion_cita_template.html', context)