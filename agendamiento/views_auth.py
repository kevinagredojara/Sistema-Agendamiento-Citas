"""Vistas de autenticación personalizadas (login y logout)."""

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import reverse_lazy

class CustomLoginView(auth_views.LoginView):
    """Vista de login personalizada con redirección según rol y seguridad de sesiones."""
    template_name = 'agendamiento/login.html'

    def dispatch(self, request, *args, **kwargs):
        """Redirige usuarios autenticados a su dashboard correspondiente."""
        if request.user.is_authenticated:
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
                messages.info(request, "Ya tienes una sesión activa.")
                return redirect('pagina_inicio')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Configura la sesión con seguridad y muestra mensaje de bienvenida personalizado."""
        response = super().form_valid(form)
        request = self.request

        # Configurar seguridad de la sesión
        request.session.cycle_key()
        request.session.set_expiry(0)
        request.session['login_timestamp'] = request.session.session_key

        # Mensaje de bienvenida según tipo de usuario
        user = form.get_user()
        nombre = user.get_full_name() or user.username
        if hasattr(user, 'asesor_perfil'):
            messages.success(request, f"Bienvenido, {nombre}. Sesión iniciada como Asesor de Servicio.")
        elif hasattr(user, 'profesional_perfil'):
            messages.success(request, f"Bienvenido, {nombre}. Sesión iniciada como Profesional de la Salud.")
        elif hasattr(user, 'paciente_perfil'):
            messages.success(request, f"Bienvenido, {nombre}. Sesión iniciada como Paciente.")
        else:
            messages.success(request, f"Bienvenido, {nombre}.")

        return response

    def get_success_url(self):
        """Determina la URL de redirección post-login según el tipo de usuario."""
        user = self.request.user

        # Verificar si hay un 'next' en la URL
        next_url = self.get_redirect_url()
        if next_url:
            return next_url

        # Redirigir según tipo de usuario
        if hasattr(user, 'asesor_perfil'):
            return reverse_lazy('agendamiento:dashboard_asesor')
        elif hasattr(user, 'profesional_perfil'):
            return reverse_lazy('agendamiento:dashboard_profesional')
        elif hasattr(user, 'paciente_perfil'):
            return reverse_lazy('agendamiento:dashboard_paciente')
        else:
            return reverse_lazy('pagina_inicio')



class CustomLogoutView(auth_views.LogoutView):
    """Vista de logout personalizada que limpia la sesión de manera segura."""
    next_page = reverse_lazy('pagina_inicio')

    def dispatch(self, request, *args, **kwargs):
        """Limpia la sesión de manera segura antes del logout."""
        if request.user.is_authenticated:
            request.session.flush()
            messages.success(request, "Sesión cerrada correctamente. ¡Hasta pronto!")

        return super().dispatch(request, *args, **kwargs)
