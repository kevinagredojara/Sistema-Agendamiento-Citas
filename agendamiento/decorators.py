"""
Decoradores personalizados para control de acceso basado en roles.
Implementa validaciones de perfiles: Asesor, Profesional y Paciente.
"""
from functools import wraps
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse_lazy

# URL de redirección cuando un usuario intenta acceder a un rol que no le corresponde
ACCESO_DENEGADO_ROL_URL = reverse_lazy('pagina_inicio')


# ============================================================================
# ASESOR DE SERVICIO
# ============================================================================

def es_asesor(user):
    """
    Verifica si el usuario tiene perfil de AsesorServicio.
    Related name: 'asesor_perfil'
    """
    return hasattr(user, 'asesor_perfil') and user.asesor_perfil is not None


def asesor_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorador que requiere usuario autenticado con perfil de Asesor.
    Redirige al login si no está autenticado, o a inicio si no es asesor.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Validar autenticación
        if not request.user.is_authenticated:
            actual_login_url = login_url or getattr(settings, 'LOGIN_URL', None)
            if not actual_login_url:
                actual_login_url = reverse_lazy('agendamiento:login')
            
            return redirect_to_login(
                request.get_full_path(),
                actual_login_url,
                redirect_field_name
            )
        
        # Validar rol de asesor
        if not es_asesor(request.user):
            return redirect(ACCESO_DENEGADO_ROL_URL)
        
        return view_func(request, *args, **kwargs)
    
    if view_func:
        return _wrapped_view
    return _wrapped_view


# ============================================================================
# PROFESIONAL DE LA SALUD
# ============================================================================

def es_profesional(user):
    """
    Verifica si el usuario tiene perfil de ProfesionalSalud.
    Related name: 'profesional_perfil'
    """
    return hasattr(user, 'profesional_perfil') and user.profesional_perfil is not None


def profesional_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorador que requiere usuario autenticado con perfil de Profesional.
    Redirige al login si no está autenticado, o a inicio si no es profesional.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Validar autenticación
        if not request.user.is_authenticated:
            actual_login_url = login_url or getattr(settings, 'LOGIN_URL', None)
            if not actual_login_url:
                actual_login_url = reverse_lazy('agendamiento:login')
            
            return redirect_to_login(
                request.get_full_path(),
                actual_login_url,
                redirect_field_name
            )
        
        # Validar rol de profesional
        if not es_profesional(request.user):
            return redirect(ACCESO_DENEGADO_ROL_URL)
        
        return view_func(request, *args, **kwargs)
    
    if view_func:
        return _wrapped_view
    return _wrapped_view


# ============================================================================
# PACIENTE
# ============================================================================

def es_paciente(user):
    """
    Verifica si el usuario tiene perfil de Paciente.
    Related name: 'paciente_perfil'
    """
    return hasattr(user, 'paciente_perfil') and user.paciente_perfil is not None


def paciente_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorador que requiere usuario autenticado con perfil de Paciente.
    Redirige al login si no está autenticado, o a inicio si no es paciente.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Validar autenticación
        if not request.user.is_authenticated:
            actual_login_url = login_url or getattr(settings, 'LOGIN_URL', None)
            if not actual_login_url:
                actual_login_url = reverse_lazy('agendamiento:login')
            
            return redirect_to_login(
                request.get_full_path(),
                actual_login_url,
                redirect_field_name
            )
        
        # Validar rol de paciente
        if not es_paciente(request.user):
            return redirect(ACCESO_DENEGADO_ROL_URL)
        
        return view_func(request, *args, **kwargs)
    
    if view_func:
        return _wrapped_view
    return _wrapped_view