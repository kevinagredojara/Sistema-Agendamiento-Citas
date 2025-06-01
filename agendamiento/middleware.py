# agendamiento/middleware.py
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

class SessionSecurityMiddleware:
    """
    Middleware para mejorar la seguridad de las sesiones.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Excluir rutas del admin de Django para superusuarios
        if request.path.startswith('/admin/') and request.user.is_authenticated and request.user.is_superuser:
            response = self.get_response(request)
            return response
        
        # Verificar si el usuario está autenticado
        if request.user.is_authenticated:
            # Verificar si la sesión ha expirado por inactividad
            if self.is_session_expired(request):
                self.handle_expired_session(request)
                return redirect(reverse('agendamiento:login'))
            
            # Actualizar el último acceso
            self.update_last_activity(request)
        
        response = self.get_response(request)
        return response

    def is_session_expired(self, request):
        """
        Verifica si la sesión ha expirado por inactividad.
        """
        last_activity = request.session.get('last_activity')
        if last_activity:
            # Convertir de string a datetime si es necesario
            if isinstance(last_activity, str):
                try:
                    last_activity = timezone.datetime.fromisoformat(last_activity)
                except ValueError:
                    return True  # Si hay error en el formato, considerar expirada
            
            # Verificar si han pasado más de 2 horas de inactividad
            if timezone.now() - last_activity > timedelta(hours=2):
                return True
        
        return False

    def update_last_activity(self, request):
        """
        Actualiza el timestamp de la última actividad del usuario.
        """
        request.session['last_activity'] = timezone.now().isoformat()

    def handle_expired_session(self, request):
        """
        Maneja una sesión expirada de manera segura.
        """
        # Cerrar la sesión del usuario
        logout(request)
        
        # Limpiar la sesión completamente
        request.session.flush()
        
        # Agregar mensaje informativo solo si MessageMiddleware está disponible
        try:
            messages.warning(request, "Tu sesión ha expirado por inactividad. Por favor, inicia sesión nuevamente.")
        except Exception:
            # Si no se pueden agregar mensajes, continuar sin el mensaje
            pass


class SessionIntegrityMiddleware:
    """
    Middleware para verificar la integridad de las sesiones.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Excluir rutas del admin de Django para superusuarios
        if request.path.startswith('/admin/') and request.user.is_authenticated and request.user.is_superuser:
            response = self.get_response(request)
            return response
        
        # Verificar integridad de la sesión antes de procesar la request
        if request.user.is_authenticated:
            if not self.verify_session_integrity(request):
                self.invalidate_session(request)
                return redirect(reverse('agendamiento:login'))
        
        response = self.get_response(request)
        return response

    def verify_session_integrity(self, request):
        """
        Verifica que la sesión sea válida y no haya sido comprometida.
        """
        # Verificar que existe el timestamp de login
        login_timestamp = request.session.get('login_timestamp')
        if not login_timestamp:
            return False
        
        # Verificar que el usuario sigue teniendo el perfil correcto
        try:
            user = request.user
            # Verificar que el usuario sigue activo
            if not user.is_active:
                return False
              # Verificar que el usuario sigue teniendo un perfil válido
            has_profile = (
                user.is_superuser or  # Permitir acceso a superusuarios/administradores
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
        Invalida una sesión comprometida.
        """
        logout(request)
        request.session.flush()
        
        # Agregar mensaje de error solo si MessageMiddleware está disponible
        try:
            messages.error(request, "Por seguridad, tu sesión ha sido invalidada. Por favor, inicia sesión nuevamente.")
        except Exception:
            # Si no se pueden agregar mensajes, continuar sin el mensaje
            pass
