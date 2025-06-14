# agendamiento/urls.py
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views
from . import views_asesor
from . import views_profesional
from . import views_paciente
from . import views_auth

app_name = 'agendamiento'

urlpatterns = [
    path('login/', views_auth.CustomLoginView.as_view(), name='login'),
    path('logout/', views_auth.CustomLogoutView.as_view(), name='logout'),

    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='agendamiento/password_change_form.html',
             success_url=reverse_lazy('agendamiento:password_change_done')
         ),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='agendamiento/password_change_done.html'
         ),
         name='password_change_done'),

    path('dashboard/asesor/', views_asesor.dashboard_asesor, name='dashboard_asesor'), 
    path('dashboard/profesional/', views.dashboard_profesional, name='dashboard_profesional'), 
    path('dashboard/paciente/', views.dashboard_paciente, name='dashboard_paciente'), 

    path('paciente/registrar/', views_asesor.registrar_paciente, name='registrar_paciente'),
    path('pacientes/', views_asesor.listar_pacientes, name='listar_pacientes'),
    path('paciente/<int:paciente_id>/actualizar/', views_asesor.actualizar_paciente, name='actualizar_paciente'),

    path('consultar-disponibilidad/', views_asesor.consultar_disponibilidad, name='consultar_disponibilidad'),

    path('agendar-cita/seleccionar-paciente/<int:profesional_id>/<str:fecha_seleccionada_str>/<str:hora_inicio_slot_str>/', 
         views_asesor.seleccionar_paciente_para_cita, 
         name='seleccionar_paciente_para_cita'),

    path('citas-gestionadas/', views_asesor.visualizar_citas_gestionadas, name='visualizar_citas_gestionadas'),

    path('cita/<int:cita_id>/modificar/', views_asesor.modificar_cita, name='modificar_cita'),
    path('cita/<int:cita_id>/modificar/confirmar/', views_asesor.confirmar_modificacion_cita, name='confirmar_modificacion_cita'),

    path('cita/<int:cita_id>/cancelar/confirmar/', views_asesor.confirmar_cancelacion_cita, name='confirmar_cancelacion_cita'),
    path('cita/<int:cita_id>/cancelar/ejecutar/', views_asesor.ejecutar_cancelacion_cita, name='ejecutar_cancelacion_cita'),
    
    path('profesional/agenda/', views_profesional.ver_agenda_profesional, name='ver_agenda_profesional'),
    path('profesional/cita/<int:cita_id>/detalles-paciente/', views_profesional.ver_detalles_paciente_cita, name='ver_detalles_paciente_cita'),
    path('profesional/cita/<int:cita_id>/registrar-asistencia/', views_profesional.registrar_asistencia_cita, name='registrar_asistencia_cita'),
    path('profesional/cita/<int:cita_id>/asistencia/confirmar/', views_profesional.confirmar_asistencia_cita, name='confirmar_asistencia_cita'),

    # URLs del Paciente
    path('paciente/mis-citas/historial/', views_paciente.ver_historial_citas, name='ver_historial_citas_paciente'),
    path('paciente/mis-citas/proximas/', views_paciente.ver_proximas_citas, name='ver_proximas_citas_paciente'),
    
    # NUEVAS URLs PARA "ACTUALIZAR MIS DATOS DE CONTACTO" DEL PACIENTE (HU-PAC-002 - Nuevo Enfoque) 👇
    path('paciente/perfil/actualizar-datos/', views_paciente.actualizar_datos_paciente, name='actualizar_datos_paciente'),
    path('paciente/perfil/actualizacion-exitosa/', views_paciente.actualizacion_datos_exitosa, name='actualizacion_datos_exitosa_paciente'),
]