# agendamiento/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User 
from django.utils import timezone
from datetime import date, timedelta, datetime, time 

from .models import Paciente, ProfesionalSalud, AsesorServicio, Especialidad, Cita
from .forms import PacienteForm 

# --- Pruebas de Acceso a Dashboards (Existentes) ---
class DashboardPacienteAccessTests(TestCase):
    """
    Pruebas para verificar el acceso al Dashboard del Paciente.
    """
    def setUp(self):
        self.dashboard_paciente_url = reverse('agendamiento:dashboard_paciente')
        self.login_url = reverse('agendamiento:login')

    def test_dashboard_paciente_redirects_unauthenticated_user_to_login(self):
        """
        Verifica que un usuario no autenticado que intenta acceder al dashboard del paciente
        es redirigido a la página de login.
        """
        response = self.client.get(self.dashboard_paciente_url)
        self.assertEqual(response.status_code, 302)
        expected_redirect_url = f'{self.login_url}?next={self.dashboard_paciente_url}'
        self.assertRedirects(response, expected_redirect_url,
                             msg_prefix="Redirección incorrecta para usuario no autenticado en dashboard_paciente.")
        # print(f"\n[TEST OK] test_dashboard_paciente_redirects_unauthenticated_user_to_login: Pasó correctamente.")

class DashboardAsesorAccessTests(TestCase):
    """
    Pruebas para verificar el acceso al Dashboard del Asesor.
    """
    def setUp(self):
        self.dashboard_asesor_url = reverse('agendamiento:dashboard_asesor')
        self.login_url = reverse('agendamiento:login')
        self.home_url = '/' 
        
        self.test_user_paciente = User.objects.create_user(username='pacienteprueba_dsas', password='password123', first_name='Paciente', last_name='Prueba')
        self.paciente_profile = Paciente.objects.create(
            user_account=self.test_user_paciente,
            tipo_documento='CC', numero_documento='12345670', # Documento único
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
        self.client.login(username='pacienteprueba_dsas', password='password123')
        response = self.client.get(self.dashboard_asesor_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_url, 
                             msg_prefix="Redirección incorrecta desde dashboard_asesor para Paciente no autorizado. Se esperaba '/'",
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
        self.asesor_user = User.objects.create_user(username='asesortest_vpc', password='password123', first_name='Asesor', last_name='PruebaVPCA')
        self.asesor_profile = AsesorServicio.objects.create(user_account=self.asesor_user) 
        self.proximas_citas_url = reverse('agendamiento:ver_proximas_citas_paciente')
        self.home_url = '/'

    def test_asesor_redirected_from_paciente_proximas_citas(self):
        self.client.login(username='asesortest_vpc', password='password123')
        response = self.client.get(self.proximas_citas_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_url, 
                             msg_prefix="Redirección incorrecta para Asesor no autorizado en vista de paciente. Se esperaba '/'",
                             target_status_code=200)
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
        self.asesor_user = User.objects.create_user(username='superasesor_rp', password='password123', first_name='Super', last_name='AsesorRP')
        self.asesor_profile = AsesorServicio.objects.create(user_account=self.asesor_user)
        self.registrar_paciente_url = reverse('agendamiento:registrar_paciente')
        self.dashboard_asesor_url = reverse('agendamiento:dashboard_asesor')

    def test_registrar_paciente_successful_creation_and_redirect(self):
        self.client.login(username='superasesor_rp', password='password123')
        user_data_prefix = 'user-'; paciente_data_prefix = 'paciente-'
        post_data = {
            f'{user_data_prefix}username': 'nuevopaciente_rp', f'{user_data_prefix}first_name': 'NuevoRP',
            f'{user_data_prefix}last_name': 'PacienteRP', f'{user_data_prefix}email': 'nuevo.pacienterp@example.com',
            f'{user_data_prefix}password': 'ClaveValida1', # Ajustar si las reglas de contraseña son diferentes
            f'{paciente_data_prefix}tipo_documento': 'CC', f'{paciente_data_prefix}numero_documento': '76543210',
            f'{paciente_data_prefix}fecha_nacimiento': '1990-01-01', f'{paciente_data_prefix}telefono_contacto': '3219876543'
        }
        response = self.client.post(self.registrar_paciente_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.dashboard_asesor_url, msg_prefix="Redirección incorrecta tras registrar paciente.")
        self.assertTrue(User.objects.filter(username='nuevopaciente_rp').exists())
        user_creado = User.objects.get(username='nuevopaciente_rp')
        self.assertTrue(Paciente.objects.filter(user_account=user_creado, numero_documento='76543210').exists())
        # print(f"\n[TEST OK] test_registrar_paciente_successful_creation_and_redirect: Pasó correctamente.")

class VerProximasCitasViewTests(TestCase):
    def setUp(self):
        self.paciente_user = User.objects.create_user(username='pacientefuturo_vpc', password='password123', first_name='FuturoVPC', last_name='PacienteVPC')
        self.paciente_profile = Paciente.objects.create(
            user_account=self.paciente_user, tipo_documento='CC', 
            numero_documento='112233445', fecha_nacimiento='1995-01-01' )
        self.especialidad = Especialidad.objects.create(nombre_especialidad="CardiologíaTestVPC", duracion_consulta_minutos=30)
        self.profesional_user = User.objects.create_user(username='drcorazontest_vpc', password='password123')
        self.profesional = ProfesionalSalud.objects.create(user_account=self.profesional_user, especialidad=self.especialidad)
        ahora = timezone.now(); duracion = timedelta(minutes=self.especialidad.duracion_consulta_minutos)
        fecha_inicio_1 = ahora + timedelta(days=5)
        self.cita_futura_programada = Cita.objects.create(
            paciente=self.paciente_profile, profesional=self.profesional,
            fecha_hora_inicio_cita=fecha_inicio_1, fecha_hora_fin_cita=fecha_inicio_1 + duracion, 
            estado_cita='Programada')
        fecha_inicio_2 = ahora - timedelta(days=5)
        self.cita_pasada_programada = Cita.objects.create(
            paciente=self.paciente_profile, profesional=self.profesional,
            fecha_hora_inicio_cita=fecha_inicio_2, fecha_hora_fin_cita=fecha_inicio_2 + duracion, 
            estado_cita='Programada')
        fecha_inicio_3 = ahora + timedelta(days=3)
        self.cita_futura_cancelada = Cita.objects.create(
            paciente=self.paciente_profile, profesional=self.profesional,
            fecha_hora_inicio_cita=fecha_inicio_3, fecha_hora_fin_cita=fecha_inicio_3 + duracion, 
            estado_cita='Cancelada')
        self.proximas_citas_url = reverse('agendamiento:ver_proximas_citas_paciente')

    def test_ver_proximas_citas_context_and_template(self):
        self.client.login(username='pacientefuturo_vpc', password='password123')
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

# CLASE DE PRUEBA DE INTEGRACIÓN QUE ESTÁBAMOS AÑADIENDO
class AgendarNuevaCitaIntegrationTests(TestCase):
    """
    Pruebas de integración para el flujo completo de agendamiento de una nueva cita
    por parte de un Asesor de Servicio.
    """
    def setUp(self):
        # 1. Crear Asesor de Servicio
        self.asesor_user = User.objects.create_user(username='asesor_integral_anc', password='password123', first_name='AsesorIntANC', last_name='PruebasANC')
        self.asesor_profile = AsesorServicio.objects.create(user_account=self.asesor_user)

        # 2. Crear Paciente
        self.paciente_user = User.objects.create_user(username='paciente_paracita_anc', password='password123', first_name='PacienteANC', last_name='ParaTestANC')
        self.paciente = Paciente.objects.create(
            user_account=self.paciente_user,
            tipo_documento='CC',
            numero_documento='20202021', # Documento único
            fecha_nacimiento='1992-02-02',
            telefono_contacto='3101234568'
        )

        # 3. Crear Especialidad y Profesional
        self.especialidad = Especialidad.objects.create(nombre_especialidad="Medicina General IntegraTestANC", duracion_consulta_minutos=25)
        self.profesional_user = User.objects.create_user(username='doc_general_test_anc', password='password123', first_name='DoctorGenANC', last_name='TestANC')
        self.profesional = ProfesionalSalud.objects.create(user_account=self.profesional_user, especialidad=self.especialidad)

        # 4. Datos para la cita
        self.fecha_cita = timezone.localdate() + timedelta(days=2) 
        if self.fecha_cita.weekday() >= 5: 
            self.fecha_cita += timedelta(days=(7 - self.fecha_cita.weekday()))
            
        self.hora_cita_str = "10:00" 
        
        self.seleccionar_paciente_url = reverse('agendamiento:seleccionar_paciente_para_cita', kwargs={
            'profesional_id': self.profesional.id,
            'fecha_seleccionada_str': self.fecha_cita.strftime('%Y-%m-%d'),
            'hora_inicio_slot_str': self.hora_cita_str
        })
        self.dashboard_asesor_url = reverse('agendamiento:dashboard_asesor')

    def test_asesor_agenda_cita_exitosamente(self):
        """
        Prueba el flujo completo donde un asesor agenda una cita exitosamente para un paciente.
        """
        self.client.login(username='asesor_integral_anc', password='password123')
        post_data = {
            'paciente_id_confirmado': self.paciente.id
        }
        response = self.client.post(self.seleccionar_paciente_url, data=post_data)
        self.assertEqual(response.status_code, 302, "No hubo redirección tras agendar la cita.")
        self.assertRedirects(response, self.dashboard_asesor_url,
                             msg_prefix="Redirección incorrecta tras agendar la cita.")
        self.assertTrue(Cita.objects.filter(
            paciente=self.paciente,
            profesional=self.profesional,
            estado_cita='Programada' 
        ).exists(), "La cita no fue creada en la base de datos o no tiene el estado esperado.")
        
        cita_creada = Cita.objects.get(paciente=self.paciente, profesional=self.profesional, estado_cita='Programada')
        
        hora_cita_obj = datetime.strptime(self.hora_cita_str, '%H:%M').time()
        fecha_hora_inicio_esperada = timezone.make_aware(datetime.combine(self.fecha_cita, hora_cita_obj))
        
        self.assertEqual(cita_creada.fecha_hora_inicio_cita, fecha_hora_inicio_esperada,
                         "La fecha y hora de inicio de la cita creada no es la esperada.")
        # print(f"\n[TEST OK] test_asesor_agenda_cita_exitosamente: Pasó correctamente.")


        # Añade esta clase a agendamiento/tests.py

class ModificarCitaIntegrationTests(TestCase):
    def setUp(self):
        # Configuración similar a AgendarNuevaCitaIntegrationTests:
        # 1. Asesor
        self.asesor_user = User.objects.create_user(username='asesor_modificador', password='password123')
        self.asesor_profile = AsesorServicio.objects.create(user_account=self.asesor_user)

        # 2. Paciente
        self.paciente_user = User.objects.create_user(username='paciente_modificable', password='password123')
        self.paciente = Paciente.objects.create(
            user_account=self.paciente_user, tipo_documento='CC', 
            numero_documento='30303030', fecha_nacimiento='1995-03-03',
            telefono_contacto='3111234567'
        )

        # 3. Especialidad y Dos Profesionales de la misma especialidad
        self.especialidad = Especialidad.objects.create(nombre_especialidad="Cirugía General TestMod", duracion_consulta_minutos=30)
        self.profesional_user1 = User.objects.create_user(username='doc_cirujano1', password='password123')
        self.profesional1 = ProfesionalSalud.objects.create(user_account=self.profesional_user1, especialidad=self.especialidad)
        
        self.profesional_user2 = User.objects.create_user(username='doc_cirujano2', password='password123')
        self.profesional2 = ProfesionalSalud.objects.create(user_account=self.profesional_user2, especialidad=self.especialidad) # Misma especialidad

        # 4. Crear una cita inicial programada
        self.fecha_cita_original = timezone.localdate() + timedelta(days=7)
        if self.fecha_cita_original.weekday() >= 5: # Evitar fin de semana para la prueba
            self.fecha_cita_original += timedelta(days=(7 - self.fecha_cita_original.weekday()))
        self.hora_cita_original_obj = time(14, 0)
        
        fecha_hora_inicio_original = timezone.make_aware(datetime.combine(self.fecha_cita_original, self.hora_cita_original_obj))
        self.cita_a_modificar = Cita.objects.create(
            paciente=self.paciente,
            profesional=self.profesional1,
            asesor_que_agenda=self.asesor_profile,
            fecha_hora_inicio_cita=fecha_hora_inicio_original,
            fecha_hora_fin_cita=fecha_hora_inicio_original + timedelta(minutes=self.especialidad.duracion_consulta_minutos),
            estado_cita='Programada'
        )

        # 5. Datos para la nueva cita (modificada)
        self.fecha_cita_nueva = self.fecha_cita_original + timedelta(days=1) # Un día después
        if self.fecha_cita_nueva.weekday() >= 5: # Evitar fin de semana
             self.fecha_cita_nueva += timedelta(days=(7 - self.fecha_cita_nueva.weekday()))
        self.hora_cita_nueva_str = "15:00" # Nueva hora

        self.modificar_cita_url_base = reverse('agendamiento:modificar_cita', kwargs={'cita_id': self.cita_a_modificar.id})
        self.confirmar_modificacion_url = reverse('agendamiento:confirmar_modificacion_cita', kwargs={'cita_id': self.cita_a_modificar.id})
        self.visualizar_citas_url = reverse('agendamiento:visualizar_citas_gestionadas')

    def test_asesor_modifica_cita_exitosamente(self):
        """
        Prueba el flujo completo donde un asesor modifica una cita exitosamente.
        Se cambia profesional, fecha y hora.
        """
        self.client.login(username='asesor_modificador', password='password123')

        # Paso 1: Acceder al formulario de modificación (GET) y buscar nueva disponibilidad
        # (Simulamos que el usuario ya seleccionó nuevo profesional y fecha en el form)
        url_con_params_get = f"{self.modificar_cita_url_base}?profesional={self.profesional2.id}&fecha_cita={self.fecha_cita_nueva.strftime('%Y-%m-%d')}"
        response_get_slots = self.client.get(url_con_params_get)
        self.assertEqual(response_get_slots.status_code, 200)
        self.assertIn('slots_disponibles', response_get_slots.context)
        # Aquí podríamos verificar que el slot self.hora_cita_nueva_str esté disponible,
        # pero para la prueba de integración del flujo de modificación, asumiremos que sí.

        # Paso 2: Acceder a la página de confirmación de modificación (GET)
        # Esto es lo que haría el enlace del slot de hora
        url_confirmacion_get = f"{self.confirmar_modificacion_url}?profesional_id={self.profesional2.id}&fecha_cita={self.fecha_cita_nueva.strftime('%Y-%m-%d')}&hora_cita={self.hora_cita_nueva_str}"
        response_confirm_page = self.client.get(url_confirmacion_get)
        self.assertEqual(response_confirm_page.status_code, 200)
        self.assertTemplateUsed(response_confirm_page, 'agendamiento/confirmar_modificacion_cita_template.html')

        # Paso 3: Enviar el POST desde la página de confirmación para guardar los cambios
        # La vista `modificar_cita` (POST) es la que guarda, usando los datos de la confirmación
        post_data_final = {
            'profesional_final_id': self.profesional2.id,
            'fecha_final_str': self.fecha_cita_nueva.strftime('%Y-%m-%d'),
            'hora_inicio_slot_seleccionada': self.hora_cita_nueva_str
        }
        response_post_save = self.client.post(self.modificar_cita_url_base, data=post_data_final)
        
        self.assertEqual(response_post_save.status_code, 302, "No hubo redirección tras modificar la cita.")
        self.assertRedirects(response_post_save, self.visualizar_citas_url, 
                             msg_prefix="Redirección incorrecta tras modificar la cita.")

        # Verificar que la cita fue actualizada en la BD
        cita_modificada = Cita.objects.get(id=self.cita_a_modificar.id)
        self.assertEqual(cita_modificada.profesional, self.profesional2)
        
        hora_cita_nueva_obj = datetime.strptime(self.hora_cita_nueva_str, '%H:%M').time()
        fecha_hora_inicio_nueva_esperada = timezone.make_aware(datetime.combine(self.fecha_cita_nueva, hora_cita_nueva_obj))
        self.assertEqual(cita_modificada.fecha_hora_inicio_cita, fecha_hora_inicio_nueva_esperada)
        self.assertEqual(cita_modificada.estado_cita, 'Programada') # Debe seguir programada
        
        print(f"\n[TEST OK] test_asesor_modifica_cita_exitosamente: Pasó correctamente.")


        # Añade esta clase a agendamiento/tests.py

class CancelarCitaIntegrationTests(TestCase):
    def setUp(self):
        self.asesor_user = User.objects.create_user(username='asesor_cancelador', password='password123')
        self.asesor_profile = AsesorServicio.objects.create(user_account=self.asesor_user)
        self.paciente_user = User.objects.create_user(username='paciente_cancelable', password='password123')
        self.paciente = Paciente.objects.create(
            user_account=self.paciente_user, tipo_documento='CC', 
            numero_documento='40404040', fecha_nacimiento='1998-04-04',
            telefono_contacto='3121234567'
        )
        self.especialidad = Especialidad.objects.create(nombre_especialidad="Dermatología TestCancel", duracion_consulta_minutos=20)
        self.profesional_user = User.objects.create_user(username='doc_derma_cancel', password='password123')
        self.profesional = ProfesionalSalud.objects.create(user_account=self.profesional_user, especialidad=self.especialidad)

        fecha_inicio = timezone.now() + timedelta(days=3)
        self.cita_a_cancelar = Cita.objects.create(
            paciente=self.paciente, profesional=self.profesional,
            asesor_que_agenda=self.asesor_profile,
            fecha_hora_inicio_cita=fecha_inicio,
            fecha_hora_fin_cita=fecha_inicio + timedelta(minutes=self.especialidad.duracion_consulta_minutos),
            estado_cita='Programada'
        )
        self.confirmar_cancelacion_url = reverse('agendamiento:confirmar_cancelacion_cita', kwargs={'cita_id': self.cita_a_cancelar.id})
        self.ejecutar_cancelacion_url = reverse('agendamiento:ejecutar_cancelacion_cita', kwargs={'cita_id': self.cita_a_cancelar.id})
        self.visualizar_citas_url = reverse('agendamiento:visualizar_citas_gestionadas')

    def test_asesor_cancela_cita_exitosamente(self):
        """Prueba el flujo completo donde un asesor cancela una cita exitosamente."""
        self.client.login(username='asesor_cancelador', password='password123')

        # Paso 1: Acceder a la página de confirmación de cancelación (GET)
        response_confirm_page = self.client.get(self.confirmar_cancelacion_url)
        self.assertEqual(response_confirm_page.status_code, 200)
        self.assertTemplateUsed(response_confirm_page, 'agendamiento/confirmar_cancelacion_cita_template.html')

        # Paso 2: Enviar el POST desde la página de confirmación para ejecutar la cancelación
        response_post_cancel = self.client.post(self.ejecutar_cancelacion_url)
        
        self.assertEqual(response_post_cancel.status_code, 302, "No hubo redirección tras cancelar la cita.")
        self.assertRedirects(response_post_cancel, self.visualizar_citas_url,
                             msg_prefix="Redirección incorrecta tras cancelar la cita.")

        # Verificar que la cita fue actualizada a 'Cancelada' en la BD
        cita_cancelada = Cita.objects.get(id=self.cita_a_cancelar.id)
        self.assertEqual(cita_cancelada.estado_cita, 'Cancelada')
        print(f"\n[TEST OK] test_asesor_cancela_cita_exitosamente: Pasó correctamente.")


        # Añade esta clase a agendamiento/tests.py

class RegistrarAsistenciaIntegrationTests(TestCase):
    def setUp(self):
        self.paciente_user = User.objects.create_user(username='paciente_asiste', password='password123')
        self.paciente = Paciente.objects.create(
            user_account=self.paciente_user, tipo_documento='RC', 
            numero_documento='50505050', fecha_nacimiento='2005-05-05',
            telefono_contacto='3131234567'
        )
        self.especialidad = Especialidad.objects.create(nombre_especialidad="Pediatría TestAsist", duracion_consulta_minutos=40)
        self.profesional_user = User.objects.create_user(username='doc_pediatra_asist', password='password123')
        self.profesional = ProfesionalSalud.objects.create(user_account=self.profesional_user, especialidad=self.especialidad)

        # Cita programada para ayer para que se pueda registrar asistencia
        self.fecha_cita = timezone.localdate() - timedelta(days=1)
        self.hora_cita_obj = time(11, 0)
        fecha_hora_inicio = timezone.make_aware(datetime.combine(self.fecha_cita, self.hora_cita_obj))
        
        self.cita_para_asistencia = Cita.objects.create(
            paciente=self.paciente, profesional=self.profesional,
            fecha_hora_inicio_cita=fecha_hora_inicio,
            fecha_hora_fin_cita=fecha_hora_inicio + timedelta(minutes=self.especialidad.duracion_consulta_minutos),
            estado_cita='Programada'
        )
        self.confirmar_asistencia_url = reverse('agendamiento:confirmar_asistencia_cita', kwargs={'cita_id': self.cita_para_asistencia.id})
        self.registrar_asistencia_url = reverse('agendamiento:registrar_asistencia_cita', kwargs={'cita_id': self.cita_para_asistencia.id})
        self.agenda_profesional_url_base = reverse('agendamiento:ver_agenda_profesional')


    def test_profesional_registra_asistencia_realizada(self):
        """Prueba que el profesional marca una cita como 'Realizada'."""
        self.client.login(username='doc_pediatra_asist', password='password123')

        # Paso 1: Acceder a la página de confirmación de asistencia (GET)
        # Los enlaces en la agenda pasan estado_propuesto y fecha_agenda
        url_confirmacion_get = f"{self.confirmar_asistencia_url}?estado_propuesto=Realizada&fecha_agenda={self.fecha_cita.strftime('%Y-%m-%d')}"
        response_confirm_page = self.client.get(url_confirmacion_get)
        self.assertEqual(response_confirm_page.status_code, 200)
        self.assertTemplateUsed(response_confirm_page, 'agendamiento/confirmar_asistencia_cita_template.html')
        self.assertEqual(response_confirm_page.context['estado_propuesto'], 'Realizada')

        # Paso 2: Enviar el POST desde la página de confirmación
        post_data = {'nuevo_estado': 'Realizada'}
        response_post_asistencia = self.client.post(self.registrar_asistencia_url, data=post_data)
        
        # Verificar redirección a la agenda del día de la cita
        expected_redirect_url = f"{self.agenda_profesional_url_base}?fecha_agenda={self.fecha_cita.strftime('%Y-%m-%d')}"
        self.assertEqual(response_post_asistencia.status_code, 302, "No hubo redirección tras registrar asistencia.")
        self.assertRedirects(response_post_asistencia, expected_redirect_url,
                             msg_prefix="Redirección incorrecta tras registrar asistencia.")

        cita_actualizada = Cita.objects.get(id=self.cita_para_asistencia.id)
        self.assertEqual(cita_actualizada.estado_cita, 'Realizada')
        print(f"\n[TEST OK] test_profesional_registra_asistencia_realizada: Pasó correctamente.")


        # Añade esta clase a agendamiento/tests.py

class ActualizarDatosPacienteIntegrationTests(TestCase):
    def setUp(self):
        self.paciente_user = User.objects.create_user(
            username='pac_actualiza', password='password123', 
            first_name='Juan', last_name='Perez', email='juan.perez@example.com'
        )
        self.paciente = Paciente.objects.create(
            user_account=self.paciente_user, tipo_documento='CC',
            numero_documento='60606060', fecha_nacimiento='1985-06-15',
            telefono_contacto='3005551111'
        )
        self.actualizar_datos_url = reverse('agendamiento:actualizar_datos_paciente')
        self.url_exito = reverse('agendamiento:actualizacion_datos_exitosa_paciente')
        self.dashboard_paciente_url = reverse('agendamiento:dashboard_paciente')

    def test_paciente_actualiza_datos_exitosamente(self):
        """Prueba que el paciente actualiza su email y teléfono y es redirigido a la página de éxito."""
        self.client.login(username='pac_actualiza', password='password123')

        # Paso 1: Cargar el formulario de actualización (GET)
        response_get = self.client.get(self.actualizar_datos_url)
        self.assertEqual(response_get.status_code, 200)
        self.assertContains(response_get, self.paciente_user.email)
        self.assertContains(response_get, self.paciente.telefono_contacto)

        # Paso 2: Enviar datos modificados (POST)
        nuevo_email = 'juan.nuevo@example.com'
        nuevo_telefono = '3005552222'
        post_data = {
            'email': nuevo_email,
            'telefono_contacto': nuevo_telefono
        }
        response_post = self.client.post(self.actualizar_datos_url, data=post_data)

        # Esperamos redirección a la página de éxito
        self.assertEqual(response_post.status_code, 302, "No hubo redirección tras actualizar datos.")
        self.assertRedirects(response_post, self.url_exito,
                             msg_prefix="Redirección incorrecta, se esperaba página de éxito.")

        # Verificar que los datos se actualizaron en la BD
        self.paciente_user.refresh_from_db()
        self.paciente.refresh_from_db()
        self.assertEqual(self.paciente_user.email, nuevo_email)
        self.assertEqual(self.paciente.telefono_contacto, nuevo_telefono)
        print(f"\n[TEST OK] test_paciente_actualiza_datos_exitosamente: Pasó correctamente.")

    def test_paciente_actualiza_datos_sin_cambios(self):
        """
        Prueba que si no hay cambios, se informa directamente en la página del formulario.
        """
        self.client.login(username='pac_actualiza', password='password123')
        
        # Datos POST idénticos a los iniciales
        post_data = {
            'email': self.paciente_user.email, 
            'telefono_contacto': self.paciente.telefono_contacto 
        }
        response_post = self.client.post(self.actualizar_datos_url, data=post_data)
        
        # Esperamos que se re-renderice el mismo formulario (código 200)
        self.assertEqual(response_post.status_code, 200, 
                         "Se esperaba re-renderizado del formulario tras intento sin cambios.")
        self.assertTemplateUsed(response_post, 'agendamiento/actualizar_datos_paciente_form.html')
        
        # Verificar que el mensaje 'form_message' está en el contexto y es el correcto
        self.assertIn('form_message', response_post.context)
        self.assertEqual(response_post.context['form_message'], "No se han realizado cambios en sus datos de contacto.")
        
        # Opcional: Verificar que no se haya añadido un mensaje flash de Django (ya que lo quitamos para este caso)
        # messages_in_response = list(response_post.context.get('messages', []))
        # self.assertEqual(len(messages_in_response), 0, "No debería haber mensajes flash de Django para este caso.")

        print(f"\n[TEST OK] test_paciente_actualiza_datos_sin_cambios (ajustado): Pasó correctamente.")

class PacienteCambioPasswordIntegrationTests(TestCase):
    def setUp(self):
        self.paciente_user = User.objects.create_user(
            username='paciente_cambia_pass', 
            password='PasswordInicial123!', # Contraseña inicial robusta
            first_name='Usuario', last_name='PruebaPass'
        )
        # Aseguramos que tiene el perfil Paciente para que CustomPasswordChangeView (si aún la usamos)
        # o cualquier lógica de rol lo identifique.
        self.paciente_profile = Paciente.objects.create(
            user_account=self.paciente_user, tipo_documento='CC',
            numero_documento='80808080', fecha_nacimiento='1999-12-12'
        )
        self.password_change_url = reverse('agendamiento:password_change')
        self.password_change_done_url = reverse('agendamiento:password_change_done')

    def test_paciente_cambia_password_exitosamente_con_reglas_standard(self):
        """
        Verifica que un paciente puede cambiar su contraseña a una nueva que
        cumpla las reglas estándar de Django.
        """
        self.client.login(username='paciente_cambia_pass', password='PasswordInicial123!')

        nueva_password_valida = "NuevaClaveSegura456$" 
        post_data = {
            'old_password': 'PasswordInicial123!',
            'new_password1': nueva_password_valida,
            'new_password2': nueva_password_valida
        }
        
        response = self.client.post(self.password_change_url, data=post_data)
        
        self.assertEqual(response.status_code, 302, 
            f"Cambio de contraseña falló. Errores: {response.context.get('form').errors if response.context else 'No form context'}. Esperaba 302, obtuve {response.status_code}")
        self.assertRedirects(response, self.password_change_done_url)

        # Verificar que la contraseña realmente cambió
        user_actualizado = User.objects.get(username='paciente_cambia_pass')
        self.assertTrue(user_actualizado.check_password(nueva_password_valida), 
                        "La nueva contraseña no fue guardada correctamente.")
        print(f"\n[TEST OK] test_paciente_cambia_password_exitosamente_con_reglas_standard: Pasó correctamente.")

    def test_paciente_falla_al_cambiar_password_por_ser_corta(self):
        """
        Verifica que un paciente no puede cambiar a una contraseña demasiado corta
        según las reglas estándar de Django.
        """
        self.client.login(username='paciente_cambia_pass', password='PasswordInicial123!')
        
        password_corta = "corta" 
        post_data = {
            'old_password': 'PasswordInicial123!',
            'new_password1': password_corta,
            'new_password2': password_corta
        }
        response = self.client.post(self.password_change_url, data=post_data)
        
        self.assertEqual(response.status_code, 200, "Se esperaba re-renderizado del formulario con errores.")
        
        # CORRECCIÓN AQUÍ: Obtener el formulario del contexto de la respuesta
        form_en_contexto = response.context.get('form')
        self.assertIsNotNone(form_en_contexto, "El formulario no se encontró en el contexto de la respuesta.")
        
        # Ahora usar form_en_contexto para assertFormError
        self.assertFormError(form_en_contexto, 'new_password2', 
            "Esta contraseña es demasiado corta. Debe contener al menos 8 caracteres.")
        # También podría ser 'new_password1' si el error se asocia al primer campo,
        # o incluso None para non_field_errors. 'new_password2' es donde PasswordChangeForm
        # usualmente pone los errores de validación de contraseña global.
        
        print(f"\n[TEST OK] test_paciente_falla_al_cambiar_password_por_ser_corta: Pasó correctamente.")

# agendamiento/tests.py
# ... (tus importaciones existentes) ...
# from django.contrib.messages import get_messages # Si vas a verificar el contenido exacto del mensaje

# ... (tus clases de prueba existentes) ...

class ConflictoSlotIntegrationTests(TestCase):
    def setUp(self):
        # Asesor
        self.asesor_user = User.objects.create_user(username='asesor_conflicto', password='password123')
        self.asesor = AsesorServicio.objects.create(user_account=self.asesor_user)

        # Paciente 1 y Paciente 2
        self.paciente1_user = User.objects.create_user(username='paciente_slot1', password='password123')
        self.paciente1 = Paciente.objects.create(user_account=self.paciente1_user, numero_documento='77777771', fecha_nacimiento='1990-01-01')
        
        self.paciente2_user = User.objects.create_user(username='paciente_slot2', password='password123')
        self.paciente2 = Paciente.objects.create(user_account=self.paciente2_user, numero_documento='77777772', fecha_nacimiento='1991-01-01')

        # Profesional y Especialidad
        self.especialidad = Especialidad.objects.create(nombre_especialidad="Conflictologia", duracion_consulta_minutos=30)
        self.profesional_user = User.objects.create_user(username='doc_conflicto', password='password123')
        self.profesional = ProfesionalSalud.objects.create(user_account=self.profesional_user, especialidad=self.especialidad)

        # Slot que vamos a intentar ocupar dos veces
        self.fecha_conflicto = timezone.localdate() + timedelta(days=3)
        if self.fecha_conflicto.weekday() >= 5: # Evitar fin de semana
            self.fecha_conflicto += timedelta(days=(7 - self.fecha_conflicto.weekday()))
        self.hora_conflicto_obj = time(10, 0)
        self.fecha_hora_conflicto_inicio = timezone.make_aware(datetime.combine(self.fecha_conflicto, self.hora_conflicto_obj))
        self.fecha_hora_conflicto_fin = self.fecha_hora_conflicto_inicio + timedelta(minutes=self.especialidad.duracion_consulta_minutos)

        # URL para agendar en ese slot (usaremos la vista seleccionar_paciente_para_cita)
        self.agendar_en_slot_url = reverse('agendamiento:seleccionar_paciente_para_cita', kwargs={
            'profesional_id': self.profesional.id,
            'fecha_seleccionada_str': self.fecha_conflicto.strftime('%Y-%m-%d'),
            'hora_inicio_slot_str': self.hora_conflicto_obj.strftime('%H:%M')
        })
        self.dashboard_asesor_url = reverse('agendamiento:dashboard_asesor')


    def test_agendar_cita_en_slot_ya_ocupado_falla(self):
        """
        Prueba que no se pueda agendar una nueva cita en un slot que se acaba de ocupar.
        """
        self.client.login(username='asesor_conflicto', password='password123')

        # 1. Agendamos la primera cita para el Paciente 1 en el slot de conflicto (esto debería funcionar)
        post_data_cita1 = {'paciente_id_confirmado': self.paciente1.id}
        response_cita1 = self.client.post(self.agendar_en_slot_url, data=post_data_cita1)
        self.assertEqual(response_cita1.status_code, 302, "La primera cita no se agendó correctamente.")
        self.assertTrue(Cita.objects.filter(
            paciente=self.paciente1, profesional=self.profesional, 
            fecha_hora_inicio_cita=self.fecha_hora_conflicto_inicio, estado_cita='Programada'
        ).exists(), "La primera cita no se creó como 'Programada'.")

        # 2. Intentamos agendar la segunda cita para el Paciente 2 en el MISMO slot
        post_data_cita2 = {'paciente_id_confirmado': self.paciente2.id}
        response_cita2 = self.client.post(self.agendar_en_slot_url, data=post_data_cita2)

        # 3. Verificar que la vista impidió la creación y mostró un error
        # La vista seleccionar_paciente_para_cita, si el slot está ocupado,
        # debería mostrar un mensaje de error y NO redirigir al dashboard del asesor,
        # sino probablemente re-renderizar la plantilla seleccionar_paciente_para_cita.html
        # o redirigir a consultar_disponibilidad. 
        # La lógica actual de seleccionar_paciente_para_cita es:
        # if Cita.objects.filter(...).exists(): messages.error(...) ; return render(...) 
        # O si es una condición que impide crearla antes, podría ser un redirect.
        # Si la doble verificación de slot ocupado en seleccionar_paciente_para_cita
        # redirige a 'consultar_disponibilidad' con un mensaje:
        
        # Asumiremos que si el slot está ocupado, la vista `seleccionar_paciente_para_cita`
        # añade un mensaje de error y redirige, por ejemplo, a `consultar_disponibilidad`.
        # Si redirige a la misma página con un error, el status code sería 200.
        # Revisando `seleccionar_paciente_para_cita`, si el slot está ocupado por la doble verificación:
        # `messages.error(request, f"El horario ... ya no está disponible. Intente con otro.")`
        # y NO hay redirección explícita después de este mensaje si el POST falla por esto,
        # lo que significa que se re-renderizará la plantilla `seleccionar_paciente_para_cita.html` con el error.
        
        self.assertEqual(response_cita2.status_code, 200, 
                         "Se esperaba re-renderizar la página de selección de paciente con un error de slot ocupado.")
        self.assertContains(response_cita2, "ya no está disponible", # Parte del mensaje de error esperado
                            msg_prefix="No se mostró el mensaje de error de slot ocupado.")

        # 4. Verificar que la segunda cita NO fue creada
        self.assertFalse(Cita.objects.filter(
            paciente=self.paciente2, profesional=self.profesional,
            fecha_hora_inicio_cita=self.fecha_hora_conflicto_inicio
        ).exists(), "La segunda cita (conflictiva) fue creada incorrectamente.")
        print(f"\n[TEST OK] test_agendar_cita_en_slot_ya_ocupado_falla: Pasó correctamente.")


# Añade esta clase a agendamiento/tests.py

class ModificarCitaEstadoNoPermitidoTests(TestCase):
    def setUp(self):
        self.asesor_user = User.objects.create_user(username='asesor_estado', password='password123')
        self.asesor = AsesorServicio.objects.create(user_account=self.asesor_user)
        self.paciente_user = User.objects.create_user(username='paciente_estado', password='password123')
        self.paciente = Paciente.objects.create(user_account=self.paciente_user, numero_documento='88888888', fecha_nacimiento='1990-01-01')
        self.especialidad = Especialidad.objects.create(nombre_especialidad="EstadoTest", duracion_consulta_minutos=30)
        self.profesional_user = User.objects.create_user(username='doc_estado', password='password123')
        self.profesional = ProfesionalSalud.objects.create(user_account=self.profesional_user, especialidad=self.especialidad)

        # Creamos una cita ya Cancelada
        fecha_inicio = timezone.now() + timedelta(days=10)
        self.cita_no_modificable = Cita.objects.create(
            paciente=self.paciente, profesional=self.profesional,
            fecha_hora_inicio_cita=fecha_inicio,
            fecha_hora_fin_cita=fecha_inicio + timedelta(minutes=self.especialidad.duracion_consulta_minutos),
            estado_cita='Cancelada' # Estado no permitido para modificar
        )
        self.modificar_cita_url = reverse('agendamiento:modificar_cita', kwargs={'cita_id': self.cita_no_modificable.id})
        self.visualizar_citas_url = reverse('agendamiento:visualizar_citas_gestionadas')