"""
Modelos del Sistema de Agendamiento de Citas.

Define las entidades principales: Especialidad, Paciente, ProfesionalSalud,
PlantillaHorarioMedico, AsesorServicio y Cita.
"""
from datetime import date

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


# ============================================================================
# CATÁLOGOS Y ESPECIALIDADES
# ============================================================================

class Especialidad(models.Model):
    """
    Especialidades médicas disponibles en el sistema.
    
    Cada especialidad tiene una duración estándar de consulta en minutos.
    """

    nombre_especialidad = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la Especialidad"
    )
    duracion_consulta_minutos = models.PositiveIntegerField(
        verbose_name="Duración Estándar de Consulta (minutos)"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="¿Está activa?"
    )

    def __str__(self):
        return self.nombre_especialidad

    class Meta:
        verbose_name = "Especialidad Médica"
        verbose_name_plural = "Especialidades Médicas"
        ordering = ['nombre_especialidad']


# ============================================================================
# PERFILES DE USUARIOS
# ============================================================================

class Paciente(models.Model):
    """
    Perfil de paciente del sistema.
    
    Vinculado con una cuenta de usuario (User) mediante relación OneToOne.
    Almacena datos personales y de contacto.
    """

    TIPOS_DOCUMENTO = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('RC', 'Registro Civil'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
    ]

    user_account = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='paciente_perfil',
        verbose_name="Cuenta de Usuario"
    )
    tipo_documento = models.CharField(
        max_length=30,
        choices=TIPOS_DOCUMENTO,
        verbose_name="Tipo de Documento"
    )
    numero_documento = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de Documento"
    )
    fecha_nacimiento = models.DateField(
        verbose_name="Fecha de Nacimiento"
    )
    telefono_contacto = models.CharField(
        max_length=20,
        verbose_name="Teléfono de Contacto"
    )

    @property
    def edad(self):
        """Calcula la edad del paciente basada en su fecha de nacimiento."""
        if self.fecha_nacimiento:
            today = date.today()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None

    def __str__(self):
        if hasattr(self, 'user_account') and self.user_account:
            nombre = self.user_account.first_name or ""
            apellido = self.user_account.last_name or ""
            return f"{nombre} {apellido} ({self.numero_documento})".strip()
        return f"Paciente {self.numero_documento}"

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['user_account__last_name', 'user_account__first_name']


class ProfesionalSalud(models.Model):
    """
    Perfil de profesional de salud del sistema.
    
    Vinculado con una cuenta de usuario (User) mediante relación OneToOne.
    Asociado a una especialidad médica.
    """

    user_account = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profesional_perfil',
        verbose_name="Cuenta de Usuario"
    )
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        related_name='profesionales',
        verbose_name="Especialidad"
    )
    numero_registro_prof = models.CharField(
        max_length=30,
        verbose_name="Número de Registro Profesional"
    )
    telefono_contacto_prof = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono de Contacto Profesional"
    )

    def __str__(self):
        nombre_completo = ""
        if hasattr(self, 'user_account') and self.user_account:
            nombre = self.user_account.first_name or ""
            apellido = self.user_account.last_name or ""
            nombre_completo = f"Dr(a). {nombre} {apellido}".strip()

        especialidad_nombre = ""
        if hasattr(self, 'especialidad') and self.especialidad:
            especialidad_nombre = self.especialidad.nombre_especialidad
        
        if nombre_completo and especialidad_nombre:
            return f"{nombre_completo} - {especialidad_nombre}"
        elif nombre_completo:
            return nombre_completo
        return f"Profesional ID {self.id or '(sin ID)'}"

    class Meta:
        verbose_name = "Profesional de la Salud"
        verbose_name_plural = "Profesionales de la Salud"
        ordering = ['user_account__last_name', 'user_account__first_name']


class AsesorServicio(models.Model):
    """
    Perfil de asesor de servicio del sistema.
    
    Vinculado con una cuenta de usuario (User) mediante relación OneToOne.
    Responsable de gestionar citas de pacientes.
    """

    user_account = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='asesor_perfil',
        verbose_name="Cuenta de Usuario"
    )

    def __str__(self):
        if hasattr(self, 'user_account') and self.user_account:
            nombre = self.user_account.first_name or ""
            apellido = self.user_account.last_name or ""
            return f"Asesor: {nombre} {apellido}".strip()
        return f"Asesor ID {self.id or '(sin ID)'}"

    class Meta:
        verbose_name = "Asesor de Servicio"
        verbose_name_plural = "Asesores de Servicio"
        ordering = ['user_account__last_name', 'user_account__first_name']


# ============================================================================
# HORARIOS Y CITAS
# ============================================================================

class PlantillaHorarioMedico(models.Model):
    """
    Plantilla de horarios semanales de profesionales de salud.
    
    Define bloques de tiempo disponibles por día de la semana.
    Valida que la hora de fin sea posterior a la hora de inicio.
    """

    DIAS_SEMANA = [
        (0, _('Lunes')),
        (1, _('Martes')),
        (2, _('Miércoles')),
        (3, _('Jueves')),
        (4, _('Viernes')),
        (5, _('Sábado')),
        (6, _('Domingo')),
    ]

    profesional = models.ForeignKey(
        ProfesionalSalud,
        on_delete=models.CASCADE,
        related_name='plantillas_horario',
        verbose_name="Profesional de la Salud"
    )
    dia_semana = models.IntegerField(
        choices=DIAS_SEMANA,
        verbose_name="Día de la Semana"
    )
    hora_inicio_bloque = models.TimeField(
        verbose_name="Hora de Inicio del Bloque"
    )
    hora_fin_bloque = models.TimeField(
        verbose_name="Hora de Fin del Bloque"
    )

    def __str__(self):
        return f"{self.profesional} - {self.get_dia_semana_display()} ({self.hora_inicio_bloque.strftime('%H:%M')} - {self.hora_fin_bloque.strftime('%H:%M')})"

    def clean(self):
        """Valida que la hora de fin sea posterior a la hora de inicio."""
        super().clean()
        if self.hora_inicio_bloque and self.hora_fin_bloque:
            if self.hora_fin_bloque <= self.hora_inicio_bloque:
                raise ValidationError(
                    {'hora_fin_bloque': _('La hora de finalización debe ser posterior a la hora de inicio.')}
                )

    class Meta:
        verbose_name = "Plantilla de Horario Médico"
        verbose_name_plural = "Plantillas de Horario Médico"
        unique_together = [['profesional', 'dia_semana', 'hora_inicio_bloque']]
        ordering = ['profesional', 'dia_semana', 'hora_inicio_bloque']


class Cita(models.Model):
    """
    Cita médica entre paciente y profesional de salud.
    
    Gestiona el agendamiento de citas con estados (Programada, Cancelada, Realizada, No Asistió).
    Valida que la fecha/hora de fin sea posterior a la de inicio.
    """

    ESTADOS_CITA = [
        ('Programada', 'Programada'),
        ('Cancelada', 'Cancelada'),
        ('Realizada', 'Realizada'),
        ('No_Asistio', 'No Asistió'),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='citas',
        verbose_name="Paciente"
    )
    profesional = models.ForeignKey(
        ProfesionalSalud,
        on_delete=models.PROTECT,
        related_name='citas_atendidas',
        verbose_name="Profesional de la Salud"
    )
    asesor_que_agenda = models.ForeignKey(
        AsesorServicio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='citas_agendadas',
        verbose_name="Asesor que Agenda"
    )
    fecha_hora_inicio_cita = models.DateTimeField(
        verbose_name="Fecha y Hora de Inicio de Cita"
    )
    fecha_hora_fin_cita = models.DateTimeField(
        verbose_name="Fecha y Hora de Fin de Cita"
    )
    estado_cita = models.CharField(
        max_length=25,
        choices=ESTADOS_CITA,
        default='Programada',
        verbose_name="Estado de la Cita"
    )

    def __str__(self):
        return f"Cita para {self.paciente} con {self.profesional} - {self.fecha_hora_inicio_cita.strftime('%d/%m/%Y %H:%M')}"

    def clean(self):
        """Valida que la fecha/hora de fin sea posterior a la de inicio."""
        super().clean()
        if self.fecha_hora_inicio_cita and self.fecha_hora_fin_cita:
            if self.fecha_hora_fin_cita <= self.fecha_hora_inicio_cita:
                raise ValidationError(
                    {'fecha_hora_fin_cita': _('La fecha y hora de finalización debe ser posterior a la fecha y hora de inicio.')}
                )

    class Meta:
        verbose_name = "Cita Médica"
        verbose_name_plural = "Citas Médicas"
        ordering = ['fecha_hora_inicio_cita', 'profesional']