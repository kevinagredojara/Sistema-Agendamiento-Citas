# agendamiento/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .decorators import asesor_required, profesional_required, paciente_required
# ASEGÚRATE DE QUE ConsultaDisponibilidadForm ESTÉ INCLUIDO EN LA IMPORTACIÓN
from .forms import UserForm, PacienteForm, UserUpdateForm, ConsultaDisponibilidadForm
from .models import Paciente # ProfesionalSalud y Especialidad ya se importan en forms.py si es necesario allí

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
        'user_form': user_form,
        'paciente_form': paciente_form,
        'titulo_pagina': 'Registrar Nuevo Paciente'
    }
    return render(request, 'agendamiento/registrar_paciente_form.html', context)

@login_required
@asesor_required
def listar_pacientes(request):
    pacientes = Paciente.objects.all().order_by('user_account__last_name', 'user_account__first_name')
    context = {
        'pacientes': pacientes,
        'titulo_pagina': 'Listado de Pacientes'
    }
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
        'user_form': user_form,
        'paciente_form': paciente_form,
        'paciente_a_actualizar': paciente_a_actualizar,
        'titulo_pagina': f'Actualizar Paciente: {usuario_a_actualizar.get_full_name() or usuario_a_actualizar.username}'
    }
    return render(request, 'agendamiento/actualizar_paciente_form.html', context)

# NUEVA VISTA PARA CONSULTAR DISPONIBILIDAD
@login_required
@asesor_required
def consultar_disponibilidad(request):
    # Por ahora, para la solicitud GET, simplemente mostramos el formulario.
    # En el futuro, si la solicitud GET tiene parámetros (profesional_id y fecha),
    # procesaremos esos parámetros aquí para buscar y mostrar los slots.
    # O podríamos manejar la búsqueda de slots cuando el formulario se envíe vía POST.
    # Vamos a empezar con el formulario GET y lo procesaremos con un POST o un GET con parámetros más adelante.

    form = ConsultaDisponibilidadForm() # Formulario vacío para la primera carga (GET)

    # Aquí irá la lógica para obtener y mostrar los slots disponibles
    # cuando el formulario se envíe (ej. request.GET o request.POST)
    # Por ahora, solo pasamos el formulario a la plantilla.
    slots_disponibles = None # Inicialmente no hay slots para mostrar
    profesional_seleccionado = None
    fecha_seleccionada = None

    if request.GET: # Si la solicitud es GET y tiene parámetros (después de enviar el formulario como GET)
        form = ConsultaDisponibilidadForm(request.GET) # Llenar el form con los datos enviados
        if form.is_valid():
            profesional_seleccionado = form.cleaned_data['profesional']
            fecha_seleccionada = form.cleaned_data['fecha']
            # AQUÍ IRÍA LA LÓGICA PARA BUSCAR SLOTS (PENDIENTE)
            # Ejemplo conceptual (la lógica real será más compleja):
            # slots_disponibles = buscar_slots(profesional_seleccionado, fecha_seleccionada)
            messages.info(request, f"Buscando disponibilidad para {profesional_seleccionado} en la fecha {fecha_seleccionada}. Lógica de búsqueda pendiente.")


    context = {
        'form': form,
        'titulo_pagina': 'Consultar Disponibilidad de Citas',
        'slots_disponibles': slots_disponibles,
        'profesional_seleccionado': profesional_seleccionado,
        'fecha_seleccionada': fecha_seleccionada
    }
    return render(request, 'agendamiento/consultar_disponibilidad_form.html', context)