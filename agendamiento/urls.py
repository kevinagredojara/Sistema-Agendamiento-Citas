# agendamiento/urls.py
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

# Modificamos las importaciones de las vistas
from . import views  # Para las vistas generales que quedaron en views.py
from . import views_asesor  # Para las vistas específicas del asesor

app_name = 'agendamiento'

urlpatterns = [
    # URLs de autenticación (usan auth_views de Django, no nuestras vistas personalizadas)
    path('login/', auth_views.LoginView.as_view(template_name='agendamiento/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
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

    # URLs de Dashboards y páginas generales (apuntan a views.py)
    # (pagina_inicio no estaba en tus urlpatterns, pero si la tuvieras, iría aquí referenciando views.pagina_inicio)
    # Por ejemplo, si tuvieras una URL para pagina_inicio:
    # path('', views.pagina_inicio, name='pagina_inicio'), 
    
    path('dashboard/asesor/', views_asesor.dashboard_asesor, name='dashboard_asesor'), # Apunta a views_asesor
    path('dashboard/profesional/', views.dashboard_profesional, name='dashboard_profesional'), # Apunta a views
    path('dashboard/paciente/', views.dashboard_paciente, name='dashboard_paciente'), # Apunta a views

    # URLS GESTIÓN DE PACIENTES (POR ASESOR - apuntan a views_asesor)
    path('paciente/registrar/', views_asesor.registrar_paciente, name='registrar_paciente'),
    path('pacientes/', views_asesor.listar_pacientes, name='listar_pacientes'),
    path('paciente/<int:paciente_id>/actualizar/', views_asesor.actualizar_paciente, name='actualizar_paciente'),

    # URL PARA CONSULTAR DISPONIBILIDAD (POR ASESOR - apunta a views_asesor)
    path('consultar-disponibilidad/', views_asesor.consultar_disponibilidad, name='consultar_disponibilidad'),

    # URL PARA LA PÁGINA DE SELECCIÓN DE PACIENTE PARA UNA CITA (POR ASESOR - apunta a views_asesor)
    path('agendar-cita/seleccionar-paciente/<int:profesional_id>/<str:fecha_seleccionada_str>/<str:hora_inicio_slot_str>/', 
         views_asesor.seleccionar_paciente_para_cita, 
         name='seleccionar_paciente_para_cita'),

    # URL PARA VISUALIZAR CITAS GESTIONADAS (POR ASESOR - apunta a views_asesor)
    path('citas-gestionadas/', views_asesor.visualizar_citas_gestionadas, name='visualizar_citas_gestionadas'),

    # URL PARA MODIFICAR UNA CITA (POR ASESOR - apunta a views_asesor)
    path('cita/<int:cita_id>/modificar/', views_asesor.modificar_cita, name='modificar_cita'),

    # URL PARA LA PÁGINA DE CONFIRMACIÓN DE MODIFICACIÓN DE CITA (POR ASESOR - apunta a views_asesor)
    path('cita/<int:cita_id>/modificar/confirmar/', views_asesor.confirmar_modificacion_cita, name='confirmar_modificacion_cita'),
    
    # Aquí irían futuras URLs para profesional (apuntando a views_profesional) 
    # y paciente (apuntando a views_paciente)
]