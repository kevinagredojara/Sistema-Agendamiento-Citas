# agendamiento/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User 
from django.utils import timezone
from datetime import date, timedelta

from .models import Paciente, ProfesionalSalud, AsesorServicio, Especialidad, Cita
from .forms import PacienteForm 

class DashboardPacienteAccessTests(TestCase):
    def setUp(self):
        self.dashboard_paciente_url = reverse('agendamiento:dashboard_paciente')
        self.login_url = reverse('agendamiento:login')

    def test_dashboard_paciente_redirects_unauthenticated_user_to_login(self):
        response = self.client.get(self.dashboard_paciente_url)
        self.assertEqual(response.status_code, 302)
        expected_redirect_url = f'{self.login_url}?next={self.dashboard_paciente_url}'
        self.assertRedirects(response, expected_redirect_url,
                             msg_prefix="Redirección incorrecta para usuario no autenticado en dashboard_paciente.")
        # print(f"\n[TEST OK] test_dashboard_paciente_redirects_unauthenticated_user_to_login: Pasó correctamente.")

class DashboardAsesorAccessTests(TestCase):
    def setUp(self):
        self.dashboard_asesor_url = reverse('agendamiento:dashboard_asesor')
        self.login_url = reverse('agendamiento:login')
        self.home_url = '/' 
        
        self.test_user_paciente = User.objects.create_user(username='pacienteprueba', password='password123', first_name='Paciente', last_name='Prueba')
        self.paciente_profile = Paciente.objects.create(
            user_account=self.test_user_paciente,
            tipo_documento='CC', numero_documento='1234567',
            telefono_contacto='3001234567', fecha_nacimiento='2000-01-01' 
        )

    def test_dashboard_asesor_redirects_unauthenticated_user_to_login(self):
        response = self.client.get(self.dashboard_asesor_url)
        self.assertEqual(response.status_code, 302)
        expected_redirect_url = f'{self.login_url}?next={self.dashboard_asesor_url}'
        self.assertRedirects(response, expected_redirect_url,
                             msg_prefix="Redirección incorrecta desde dashboard_asesor para usuario no autenticado.")
        # print(f"\n[TEST OK] test_dashboard_asesor_redirects_unauthenticated_user_to_login: Pasó correctamente.")

    def test_dashboard_asesor_redirects_logged_in_paciente(self):
        self.client.login(username='pacienteprueba', password='password123')
        response = self.client.get(self.dashboard_asesor_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_url, # Espera redirección a home_url ('/')
                             msg_prefix="Redirección incorrecta desde dashboard_asesor para Paciente no autorizado.",
                             target_status_code=200) 
        # print(f"\n[TEST OK] test_dashboard_asesor_redirects_logged_in_paciente: Pasó correctamente (esperando redirección a '/').")


class DashboardProfesionalAccessTests(TestCase):
    def setUp(self):
        self.dashboard_profesional_url = reverse('agendamiento:dashboard_profesional')
        self.login_url = reverse('agendamiento:login')

    def test_dashboard_profesional_redirects_unauthenticated_user_to_login(self):
        response = self.client.get(self.dashboard_profesional_url)
        self.assertEqual(response.status_code, 302)
        expected_redirect_url = f'{self.login_url}?next={self.dashboard_profesional_url}'
        self.assertRedirects(response, expected_redirect_url,
                             msg_prefix="Redirección incorrecta desde dashboard_profesional para usuario no autenticado.")
        # print(f"\n[TEST OK] test_dashboard_profesional_redirects_unauthenticated_user_to_login: Pasó correctamente.")

class VerProximasCitasAccessTests(TestCase):
    def setUp(self):
        self.asesor_user = User.objects.create_user(username='asesortest', password='password123', first_name='Asesor', last_name='Prueba')
        self.asesor_profile = AsesorServicio.objects.create(user_account=self.asesor_user) # Asumiendo que existe AsesorServicio

        self.proximas_citas_url = reverse('agendamiento:ver_proximas_citas_paciente')
        self.home_url = '/' # A donde probablemente redirige si el rol no es correcto pero está logueado

    def test_asesor_redirected_from_paciente_proximas_citas(self):
        """Verifica que un Asesor logueado es redirigido si intenta acceder a 'ver_proximas_citas_paciente'."""
        self.client.login(username='asesortest', password='password123')
        response = self.client.get(self.proximas_citas_url)
        
        self.assertEqual(response.status_code, 302)
        # AJUSTE: Esperamos que redirija a self.home_url (que es '/')
        self.assertRedirects(response, self.home_url, 
                             msg_prefix="Redirección incorrecta para Asesor no autorizado en vista de paciente.",
                             target_status_code=200) # Asumiendo que la home page da 200
        # print(f"\n[TEST OK] test_asesor_redirected_from_paciente_proximas_citas: Pasó correctamente.")

class PacienteFormValidationTests(TestCase):
    def test_fecha_nacimiento_cannot_be_future_date(self):
        future_date = timezone.localdate() + timedelta(days=1)
        data = {
            'tipo_documento': 'CC', 'numero_documento': '12345678',
            'fecha_nacimiento': future_date.strftime('%Y-%m-%d'),
            'telefono_contacto': '3001234560' }
        form = PacienteForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_nacimiento', form.errors)
        self.assertEqual(form.errors['fecha_nacimiento'][0], "La fecha de nacimiento no puede ser una fecha futura.")
        # print(f"\n[TEST OK] test_fecha_nacimiento_cannot_be_future_date: Pasó correctamente.")

    def test_fecha_nacimiento_valid_past_date(self):
        past_date = date(2000, 5, 15)
        data = {
            'tipo_documento': 'CC', 'numero_documento': '12345678',
            'fecha_nacimiento': past_date.strftime('%Y-%m-%d'),
            'telefono_contacto': '3001234560' }
        form = PacienteForm(data=data)
        self.assertTrue(form.is_valid(), f"Formulario no fue válido. Errores: {form.errors.as_json()}")
        # print(f"\n[TEST OK] test_fecha_nacimiento_valid_past_date: Pasó correctamente.")

class RegistrarPacienteViewTests(TestCase):
    def setUp(self):
        self.asesor_user = User.objects.create_user(username='superasesor', password='password123', first_name='Super', last_name='Asesor')
        self.asesor_profile = AsesorServicio.objects.create(user_account=self.asesor_user)
        self.registrar_paciente_url = reverse('agendamiento:registrar_paciente')
        self.dashboard_asesor_url = reverse('agendamiento:dashboard_asesor')

    def test_registrar_paciente_successful_creation_and_redirect(self):
        self.client.login(username='superasesor', password='password123')
        user_data_prefix = 'user-'; paciente_data_prefix = 'paciente-'
        post_data = {
            f'{user_data_prefix}username': 'nuevopaciente', f'{user_data_prefix}first_name': 'Nuevo',
            f'{user_data_prefix}last_name': 'Paciente', f'{user_data_prefix}email': 'nuevo.paciente@example.com',
            f'{user_data_prefix}password': 'PinValido123', 
            f'{paciente_data_prefix}tipo_documento': 'CC', f'{paciente_data_prefix}numero_documento': '7654321',
            f'{paciente_data_prefix}fecha_nacimiento': '1990-01-01', f'{paciente_data_prefix}telefono_contacto': '3219876543'
        }
        response = self.client.post(self.registrar_paciente_url, data=post_data)
        self.assertEqual(response.status_code, 302, "No hubo redirección tras el POST exitoso.")
        self.assertRedirects(response, self.dashboard_asesor_url, msg_prefix="Redirección incorrecta tras registrar paciente.")
        self.assertTrue(User.objects.filter(username='nuevopaciente').exists(), "Usuario no fue creado.")
        user_creado = User.objects.get(username='nuevopaciente')
        self.assertTrue(Paciente.objects.filter(user_account=user_creado, numero_documento='7654321').exists(), "Perfil de Paciente no fue creado.")
        # print(f"\n[TEST OK] test_registrar_paciente_successful_creation_and_redirect: Pasó correctamente.")

class VerProximasCitasViewTests(TestCase):
    def setUp(self):
        self.paciente_user = User.objects.create_user(username='pacientefuturo', password='password123', first_name='Futuro', last_name='Paciente')
        self.paciente_profile = Paciente.objects.create(
            user_account=self.paciente_user, 
            tipo_documento='CC', 
            numero_documento='11223344',
            fecha_nacimiento='1995-01-01' 
        )
        
        self.especialidad = Especialidad.objects.create(nombre_especialidad="Cardiología Test", duracion_consulta_minutos=30)
        self.profesional_user = User.objects.create_user(username='drcorazontest', password='password123')
        self.profesional = ProfesionalSalud.objects.create(user_account=self.profesional_user, especialidad=self.especialidad)
        
        ahora = timezone.now()
        duracion = timedelta(minutes=self.especialidad.duracion_consulta_minutos)

        # CORRECCIÓN: Añadir fecha_hora_fin_cita al crear Cita aquí 👇
        fecha_inicio_1 = ahora + timedelta(days=5)
        self.cita_futura_programada = Cita.objects.create(
            paciente=self.paciente_profile, profesional=self.profesional,
            fecha_hora_inicio_cita=fecha_inicio_1, 
            fecha_hora_fin_cita=fecha_inicio_1 + duracion, # Añadido
            estado_cita='Programada'
        )
        
        fecha_inicio_2 = ahora - timedelta(days=5)
        self.cita_pasada_programada = Cita.objects.create(
            paciente=self.paciente_profile, profesional=self.profesional,
            fecha_hora_inicio_cita=fecha_inicio_2,
            fecha_hora_fin_cita=fecha_inicio_2 + duracion, # Añadido
            estado_cita='Programada'
        )

        fecha_inicio_3 = ahora + timedelta(days=3)
        self.cita_futura_cancelada = Cita.objects.create(
            paciente=self.paciente_profile, profesional=self.profesional,
            fecha_hora_inicio_cita=fecha_inicio_3, 
            fecha_hora_fin_cita=fecha_inicio_3 + duracion, # Añadido
            estado_cita='Cancelada'
        )
        self.proximas_citas_url = reverse('agendamiento:ver_proximas_citas_paciente')

    def test_ver_proximas_citas_context_and_template(self):
        self.client.login(username='pacientefuturo', password='password123')
        response = self.client.get(self.proximas_citas_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agendamiento/mis_proximas_citas.html')
        self.assertIn('proximas_citas', response.context)
        citas_en_contexto = response.context['proximas_citas']
        self.assertEqual(len(citas_en_contexto), 1)
        self.assertIn(self.cita_futura_programada, citas_en_contexto)
        self.assertNotIn(self.cita_pasada_programada, citas_en_contexto)
        self.assertNotIn(self.cita_futura_cancelada, citas_en_contexto)
        # print(f"\n[TEST OK] test_ver_proximas_citas_context_and_template: Pasó correctamente.")