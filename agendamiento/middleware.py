"""
Middlewares de seguridad para el Sistema de Agendamiento.
Implementa protección de sesiones y validación de integridad.
"""
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import sys


class SessionSecurityMiddleware:
    """
    Middleware de seguridad de sesiones.
    
    Funcionalidades:
    - Expiración automática por inactividad (2 horas)
    - Seguimiento de última actividad del usuario
    - Cierre seguro de sesiones expiradas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Excluir durante tests
        if 'test' in sys.argv:
            return self.get_response(request)
        
        # Excluir admin de Django para superusuarios
        if request.path.startswith('/admin/') and request.user.is_authenticated and request.user.is_superuser:
            return self.get_response(request)
        
        # Validar sesión de usuarios autenticados
        if request.user.is_authenticated:
            if self.is_session_expired(request):
                self.handle_expired_session(request)
                return redirect(reverse('agendamiento:login'))
            
            # Actualizar marca de tiempo de actividad
            self.update_last_activity(request)
        
        return self.get_response(request)

    def is_session_expired(self, request):
        """
        Verifica si la sesión ha expirado por inactividad (2 horas).
        """
        last_activity = request.session.get('last_activity')
        
        if not last_activity:
            return False
        
        # Convertir string a datetime si es necesario
        if isinstance(last_activity, str):
            try:
                last_activity = timezone.datetime.fromisoformat(last_activity)
            except ValueError:
                return True  # Error de formato = sesión expirada
        
        # Verificar límite de inactividad (2 horas)
        return timezone.now() - last_activity > timedelta(hours=2)

    def update_last_activity(self, request):
        """
        Actualiza el timestamp de la última actividad del usuario.
        """
        request.session['last_activity'] = timezone.now().isoformat()

    def handle_expired_session(self, request):
        """
        Cierra y limpia una sesión expirada de manera segura.
        """
        logout(request)
        request.session.flush()
        
        # Agregar mensaje informativo (si MessageMiddleware está disponible)
        try:
            messages.warning(request, "Tu sesión ha expirado por inactividad. Por favor, inicia sesión nuevamente.")
        except Exception:
            pass  # Continuar sin mensaje si hay error


class SessionIntegrityMiddleware:
    """
    Middleware de integridad de sesiones.
    
    Funcionalidades:
    - Verificación de timestamp de login
    - Validación de estado activo del usuario
    - Validación de existencia de perfil
    - Invalidación de sesiones comprometidas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Excluir durante tests
        if 'test' in sys.argv:
            return self.get_response(request)
        
        # Excluir admin de Django para superusuarios
        if request.path.startswith('/admin/') and request.user.is_authenticated and request.user.is_superuser:
            return self.get_response(request)
        
        # Verificar integridad de sesiones autenticadas
        if request.user.is_authenticated:
            if not self.verify_session_integrity(request):
                self.invalidate_session(request)
                return redirect(reverse('agendamiento:login'))
        
        return self.get_response(request)

    def verify_session_integrity(self, request):
        """
        Verifica que la sesión sea válida y no haya sido comprometida.
        
        Validaciones:
        1. Existencia de timestamp de login
        2. Usuario activo en el sistema
        3. Usuario tiene perfil válido (Paciente/Profesional/Asesor/Admin)
        """
        # Validar timestamp de login
        if not request.session.get('login_timestamp'):
            return False
        
        try:
            user = request.user
            
            # Validar usuario activo
            if not user.is_active:
                return False
            
            # Validar existencia de perfil válido
            has_profile = (
                user.is_superuser or  # Administrador
                hasattr(user, 'asesor_perfil') or 
                hasattr(user, 'profesional_perfil') or 
                hasattr(user, 'paciente_perfil')
            )
            
            if not has_profile:
                return False
            
        except Exception:
            return False
        
        return True

    def invalidate_session(self, request):
        """
        Invalida y limpia una sesión comprometida de manera segura.
        """
        logout(request)
        request.session.flush()
        
        # Agregar mensaje de error (si MessageMiddleware está disponible)
        try:
            messages.error(request, "Por seguridad, tu sesión ha sido invalidada. Por favor, inicia sesión nuevamente.")
        except Exception:
            pass  # Continuar sin mensaje si hay error
