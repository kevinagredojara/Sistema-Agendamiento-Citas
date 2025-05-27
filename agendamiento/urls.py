# agendamiento/urls.py
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'agendamiento'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='agendamiento/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # URLs para cambio de contraseña
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

    # URLs de Dashboards
    path('dashboard/asesor/', views.dashboard_asesor, name='dashboard_asesor'),
    path('dashboard/profesional/', views.dashboard_profesional, name='dashboard_profesional'),
    path('dashboard/paciente/', views.dashboard_paciente, name='dashboard_paciente'),

    # URLS GESTIÓN DE PACIENTES (POR ASESOR)
    path('paciente/registrar/', views.registrar_paciente, name='registrar_paciente'),
    path('pacientes/', views.listar_pacientes, name='listar_pacientes'),
    path('paciente/<int:paciente_id>/actualizar/', views.actualizar_paciente, name='actualizar_paciente'),

    # URL PARA CONSULTAR DISPONIBILIDAD
    path('consultar-disponibilidad/', views.consultar_disponibilidad, name='consultar_disponibilidad'),

    # URL PARA LA PÁGINA DE SELECCIÓN DE PACIENTE PARA UNA CITA
    path('agendar-cita/seleccionar-paciente/<int:profesional_id>/<str:fecha_seleccionada_str>/<str:hora_inicio_slot_str>/', 
         views.seleccionar_paciente_para_cita, 
         name='seleccionar_paciente_para_cita'),

    # NUEVA URL PARA VISUALIZAR CITAS GESTIONADAS (HU-ASE-009) 👇
    path('citas-gestionadas/', views.visualizar_citas_gestionadas, name='visualizar_citas_gestionadas'),
]