# agendamiento/decorators.py
from functools import wraps
from django.conf import settings # Importamos settings para acceder a LOGIN_URL
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import redirect_to_login # Utilidad para redirigir al login

# URL a la que redirigir si un usuario logueado intenta acceder a una vista de un rol que no le corresponde.
# Por ahora, todos van a la página de inicio general.
ACCESO_DENEGADO_ROL_URL = reverse_lazy('pagina_inicio')

# --- Para Asesor ---
def es_asesor(user):
    """
    Verifica si un usuario (que se asume autenticado) tiene un perfil de AsesorServicio.
    El related_name para AsesorServicio.user_account es 'asesor_perfil'.
    """
    # La verificación de user.is_authenticated ya se hace en el decorador.
    return hasattr(user, 'asesor_perfil') and user.asesor_perfil is not None

def asesor_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorador para vistas que verifica que el usuario esté logueado Y sea un asesor.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            actual_login_url = login_url or getattr(settings, 'LOGIN_URL', None)
            if not actual_login_url: 
                actual_login_url = reverse_lazy('agendamiento:login')
            
            return redirect_to_login(
                request.get_full_path(),
                actual_login_url,
                redirect_field_name
            )
        
        if not es_asesor(request.user):
            return redirect(ACCESO_DENEGADO_ROL_URL)
        
        return view_func(request, *args, **kwargs)
    
    if view_func:
        return _wrapped_view
    return _wrapped_view

# --- Para Profesional de la Salud ---
def es_profesional(user):
    """
    Verifica si un usuario (que se asume autenticado) tiene un perfil de ProfesionalSalud.
    El related_name para ProfesionalSalud.user_account es 'profesional_perfil'.
    """
    return hasattr(user, 'profesional_perfil') and user.profesional_perfil is not None

def profesional_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorador para vistas que verifica que el usuario esté logueado Y sea un profesional.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            actual_login_url = login_url or getattr(settings, 'LOGIN_URL', None)
            if not actual_login_url:
                actual_login_url = reverse_lazy('agendamiento:login')
            return redirect_to_login(request.get_full_path(), actual_login_url, redirect_field_name)
        
        if not es_profesional(request.user):
            return redirect(ACCESO_DENEGADO_ROL_URL)
        
        return view_func(request, *args, **kwargs)
    
    if view_func:
        return _wrapped_view
    return _wrapped_view

# --- Para Paciente ---
def es_paciente(user):
    """
    Verifica si un usuario (que se asume autenticado) tiene un perfil de Paciente.
    El related_name para Paciente.user_account es 'paciente_perfil'.
    """
    return hasattr(user, 'paciente_perfil') and user.paciente_perfil is not None

def paciente_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorador para vistas que verifica que el usuario esté logueado Y sea un paciente.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            actual_login_url = login_url or getattr(settings, 'LOGIN_URL', None)
            if not actual_login_url:
                actual_login_url = reverse_lazy('agendamiento:login')
            return redirect_to_login(request.get_full_path(), actual_login_url, redirect_field_name)
        
        if not es_paciente(request.user):
            return redirect(ACCESO_DENEGADO_ROL_URL)
            
        return view_func(request, *args, **kwargs)
        
    if view_func:
        return _wrapped_view
    return _wrapped_view