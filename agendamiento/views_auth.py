# agendamiento/views_auth.py
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib import messages

class CustomLoginView(auth_views.LoginView):
    """
    Vista de login personalizada que redirige a usuarios ya autenticados
    a su dashboard correspondiente y maneja la seguridad de sesiones.
    """
    template_name = 'agendamiento/login.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Si el usuario ya está autenticado, redirigirlo a su dashboard
        if request.user.is_authenticated:
            # Determinar a qué dashboard redirigir según el tipo de usuario
            if hasattr(request.user, 'asesor_perfil'):
                messages.info(request, "Ya tienes una sesión activa como Asesor de Servicio.")
                return redirect('agendamiento:dashboard_asesor')
            elif hasattr(request.user, 'profesional_perfil'):
                messages.info(request, "Ya tienes una sesión activa como Profesional de la Salud.")
                return redirect('agendamiento:dashboard_profesional')
            elif hasattr(request.user, 'paciente_perfil'):
                messages.info(request, "Ya tienes una sesión activa como Paciente.")
                return redirect('agendamiento:dashboard_paciente')
            else:
                # Usuario sin perfil específico, redirigir a página de inicio
                messages.info(request, "Ya tienes una sesión activa.")
                return redirect('pagina_inicio')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Sobrescribir para configurar la sesión con mayor seguridad.
        """
        response = super().form_valid(form)
        
        # Configurar la sesión para mayor seguridad
        request = self.request
        
        # Regenerar la clave de sesión para evitar session fixation
        request.session.cycle_key()
        
        # Configurar que la sesión expire al cerrar el navegador
        request.session.set_expiry(0)  # 0 significa "expira cuando se cierre el navegador"
        
        # Agregar información de seguridad a la sesión
        request.session['login_timestamp'] = request.session.session_key
        
        # Mensaje de bienvenida personalizado según el tipo de usuario
        user = form.get_user()
        if hasattr(user, 'asesor_perfil'):
            messages.success(request, f"Bienvenido, {user.get_full_name() or user.username}. Sesión iniciada como Asesor de Servicio.")
        elif hasattr(user, 'profesional_perfil'):
            messages.success(request, f"Bienvenido, {user.get_full_name() or user.username}. Sesión iniciada como Profesional de la Salud.")
        elif hasattr(user, 'paciente_perfil'):
            messages.success(request, f"Bienvenido, {user.get_full_name() or user.username}. Sesión iniciada como Paciente.")
        else:
            messages.success(request, f"Bienvenido, {user.get_full_name() or user.username}.")
        
        return response
    
    def get_success_url(self):
        """
        Determinar a dónde redirigir después del login según el tipo de usuario.
        """
        user = self.request.user
        
        # Verificar si hay un 'next' en la URL
        next_url = self.get_redirect_url()
        if next_url:
            return next_url
        
        # Redirigir según el tipo de usuario
        if hasattr(user, 'asesor_perfil'):
            return reverse_lazy('agendamiento:dashboard_asesor')
        elif hasattr(user, 'profesional_perfil'):
            return reverse_lazy('agendamiento:dashboard_profesional')
        elif hasattr(user, 'paciente_perfil'):
            return reverse_lazy('agendamiento:dashboard_paciente')
        else:
            return reverse_lazy('pagina_inicio')


class CustomLogoutView(auth_views.LogoutView):
    """
    Vista de logout personalizada que limpia la sesión de manera segura.
    """
    next_page = reverse_lazy('pagina_inicio')
    
    def dispatch(self, request, *args, **kwargs):
        """
        Limpiar la sesión de manera segura antes del logout.
        """
        if request.user.is_authenticated:
            # Limpiar datos sensibles de la sesión
            request.session.flush()  # Elimina todos los datos de la sesión y regenera la clave
            messages.success(request, "Sesión cerrada correctamente. ¡Hasta pronto!")
        
        return super().dispatch(request, *args, **kwargs)
