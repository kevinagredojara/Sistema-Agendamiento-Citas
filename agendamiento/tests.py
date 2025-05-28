# agendamiento/tests.py
from django.test import TestCase, Client # Client nos permite simular peticiones web
from django.urls import reverse # Para obtener URLs a partir de sus nombres
from django.contrib.auth.models import User # Para crear usuarios de prueba si es necesario en el futuro
# from .models import Paciente, ProfesionalSalud, AsesorServicio # Importaremos modelos cuando los necesitemos

class DashboardPacienteAccessTests(TestCase):
    """
    Pruebas para verificar el acceso al Dashboard del Paciente.
    """

    def setUp(self):
        """
        Configuración inicial para las pruebas de esta clase.
        El cliente de prueba se crea automáticamente como self.client.
        """
        # Podríamos crear usuarios aquí si las pruebas los necesitaran logueados,
        # pero para esta primera prueba, queremos un usuario NO logueado.
        pass

    def test_dashboard_paciente_redirects_unauthenticated_user_to_login(self):
        """
        Verifica que un usuario no autenticado que intenta acceder al dashboard del paciente
        es redirigido a la página de login.
        """
        # 1. Obtener la URL del dashboard del paciente usando su nombre definido en urls.py
        #    Asumimos que la vista está en el archivo 'views.py' general de la app 'agendamiento'
        #    y que el nombre de la URL es 'dashboard_paciente'.
        #    Si la vista dashboard_paciente estuviera en, por ejemplo, views_paciente.py,
        #    y urls.py apunta a views_paciente.dashboard_paciente, esta prueba seguiría siendo válida
        #    mientras el nombre de la URL 'agendamiento:dashboard_paciente' sea correcto.
        url_dashboard_paciente = reverse('agendamiento:dashboard_paciente')

        # 2. Usar el cliente de prueba (self.client) para hacer una petición GET a esa URL.
        #    Esto simula a un usuario intentando visitar la página sin estar logueado.
        response = self.client.get(url_dashboard_paciente)

        # 3. Verificar que el código de estado de la respuesta sea 302 (Redirección).
        #    El decorador @login_required debería causar esta redirección.
        self.assertEqual(response.status_code, 302, 
                         "La vista no redirigió al usuario no autenticado.")

        # 4. Construir la URL de login esperada, incluyendo el parámetro 'next'.
        #    Django redirige a LOGIN_URL?next=/url/original/
        #    Asumimos que LOGIN_URL está configurado para 'agendamiento:login'.
        url_login = reverse('agendamiento:login')
        expected_redirect_url = f'{url_login}?next={url_dashboard_paciente}'

        # 5. Verificar que la redirección sea a la URL de login correcta.
        self.assertRedirects(response, expected_redirect_url,
                             msg_prefix="Redirección incorrecta para usuario no autenticado.")

        print(f"\n[TEST OK] test_dashboard_paciente_redirects_unauthenticated_user_to_login: Pasó correctamente.")

# Aquí podríamos añadir más clases de prueba para otras vistas o modelos.
# Por ejemplo:
# class DashboardAsesorAccessTests(TestCase):
#     # ... pruebas para el dashboard del asesor ...
#     pass

# class UserModelTests(TestCase):
#     # ... pruebas para el modelo User o perfiles ...
#     pass