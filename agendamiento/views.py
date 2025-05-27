# agendamiento/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .decorators import asesor_required, profesional_required, paciente_required
# LÍNEA DE IMPORTACIÓN DE FORMULARIOS ACTUALIZADA (si la tienes así):
from .forms import (
    UserForm, PacienteForm, UserUpdateForm, 
    ConsultaDisponibilidadForm, BuscarPacientePorDocumentoForm
)
# ASEGÚRATE DE QUE 'Cita' ESTÉ IMPORTADO. SI NO, AÑÁDELO:
from .models import Paciente, ProfesionalSalud, PlantillaHorarioMedico, Cita 
from datetime import datetime, time, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

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
    form = ConsultaDisponibilidadForm()
    slots_disponibles = []
    profesional_seleccionado = None
    fecha_seleccionada = None
    if request.GET and 'profesional' in request.GET and 'fecha' in request.GET:
        form = ConsultaDisponibilidadForm(request.GET)
        if form.is_valid():
            profesional_seleccionado = form.cleaned_data['profesional']
            fecha_seleccionada = form.cleaned_data['fecha']
            if profesional_seleccionado and fecha_seleccionada:
                dia_semana_seleccionado = fecha_seleccionada.weekday()
                plantillas = PlantillaHorarioMedico.objects.filter(
                    profesional=profesional_seleccionado,
                    dia_semana=dia_semana_seleccionado
                ).order_by('hora_inicio_bloque')
                current_tz = timezone.get_current_timezone() # America/Bogota
                
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
                elif not plantillas.exists():
                    messages.warning(request, f"{profesional_seleccionado} no tiene un horario configurado para el día seleccionado ({fecha_seleccionada.strftime('%A, %d/%m/%Y')}).")
    
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

    if 'buscar_paciente' in request.GET: 
        form_buscar_paciente = BuscarPacientePorDocumentoForm(request.GET)
        if form_buscar_paciente.is_valid():
            numero_documento = form_buscar_paciente.cleaned_data['numero_documento']
            try:
                paciente_encontrado = Paciente.objects.get(numero_documento=numero_documento, user_account__is_active=True)
                messages.success(request, f"Paciente encontrado: {paciente_encontrado.user_account.get_full_name()}")
            except Paciente.DoesNotExist:
                messages.error(request, f"No se encontró un paciente activo con el número de documento '{numero_documento}'. Puede registrarlo si es necesario.")
    else:
        form_buscar_paciente = BuscarPacientePorDocumentoForm() 

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
                    Cita.objects.create(
                        paciente=paciente_seleccionado,
                        profesional=profesional,
                        asesor_que_agenda=request.user.asesor_perfil, # ASUMIENDO QUE EL ASESOR TIENE 'asesor_perfil'
                        fecha_hora_inicio_cita=fecha_hora_inicio_cita_aware,
                        fecha_hora_fin_cita=fecha_hora_fin_cita_aware,
                        estado_cita='Programada'
                    )
                    if paciente_seleccionado.user_account.email:
                        asunto = f"Confirmación de Cita Médica - {profesional.especialidad.nombre_especialidad}"
                        mensaje_email = (
                            f"Estimado(a) {paciente_seleccionado.user_account.get_full_name()},\n\n"
                            f"Le confirmamos su cita médica para el servicio de {profesional.especialidad.nombre_especialidad} "
                            f"con el/la Dr(a). {profesional.user_account.get_full_name()}.\n\n"
                            f"Fecha: {fecha_obj.strftime('%A, %d de %B de %Y')}\n"
                            f"Hora: {hora_obj.strftime('%I:%M %p')}\n\n"
                            f"Por favor, llegue con anticipación.\n\n"
                            f"Saludos cordiales,\nIPS Medical Integral"
                        )
                        try:
                            send_mail(asunto, mensaje_email, settings.DEFAULT_FROM_EMAIL, [paciente_seleccionado.user_account.email], fail_silently=False)
                            messages.success(request, f"Cita agendada para {paciente_seleccionado} con {profesional} el {fecha_obj.strftime('%d/%m/%Y')} a las {hora_obj.strftime('%H:%M')}. Se envió correo de confirmación.")
                        except Exception as e:
                            messages.warning(request, f"Cita agendada para {paciente_seleccionado} con {profesional} el {fecha_obj.strftime('%d/%m/%Y')} a las {hora_obj.strftime('%H:%M')}. Hubo un problema al enviar el correo de confirmación: {e}")
                    else:
                        messages.success(request, f"Cita agendada para {paciente_seleccionado} con {profesional} el {fecha_obj.strftime('%d/%m/%Y')} a las {hora_obj.strftime('%H:%M')}. (El paciente no tiene email registrado para notificación).")
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

# NUEVA VISTA PARA HU-ASE-009 👇
@login_required
@asesor_required
def visualizar_citas_gestionadas(request):
    # Por ahora, listamos todas las citas. Más adelante podríamos filtrar por las que el asesor gestiona.
    # O considerar si un asesor siempre puede ver todas.
    # Para este MVP inicial, mostrar todas las citas 'Programada' o 'Realizada' podría ser un buen comienzo.
    # O simplemente todas para que pueda ver el historial completo y luego filtrar.
    
    # Ordenamos por fecha de inicio descendente (más recientes primero)
    lista_citas = Cita.objects.all().order_by('-fecha_hora_inicio_cita') 
    
    context = {
        'citas': lista_citas,
        'titulo_pagina': 'Citas Médicas Gestionadas'
    }
    # Nombre de la plantilla que crearemos en el siguiente paso:
    return render(request, 'agendamiento/visualizar_citas_gestionadas.html', context)