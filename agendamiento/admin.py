"""
Configuración del panel de administración de Django.

Define las clases ModelAdmin para personalizar la visualización y gestión
de los modelos Paciente, ProfesionalSalud, AsesorServicio, PlantillaHorarioMedico y Cita.
"""
from django.contrib import admin
from django.utils import timezone
from .models import Especialidad, Paciente, ProfesionalSalud, PlantillaHorarioMedico, AsesorServicio, Cita


# ============================================================================
# ADMINISTRACIÓN DE PACIENTES
# ============================================================================

class PacienteAdmin(admin.ModelAdmin):
    """Configuración del panel de administración para Paciente."""

    list_display = ('get_full_name', 'tipo_documento', 'numero_documento', 'telefono_contacto', 'get_email')
    search_fields = ('user_account__first_name', 'user_account__last_name', 'numero_documento', 'user_account__email')
    list_filter = ('tipo_documento',)

    @admin.display(description='Nombre Completo')
    def get_full_name(self, obj):
        """Retorna el nombre completo del paciente desde su cuenta de usuario."""
        return obj.user_account.get_full_name() or obj.user_account.username if obj.user_account else "N/A"

    @admin.display(description='Correo Electrónico')
    def get_email(self, obj):
        """Retorna el correo electrónico del paciente desde su cuenta de usuario."""
        return obj.user_account.email if obj.user_account else "N/A"


# ============================================================================
# ADMINISTRACIÓN DE PROFESIONALES DE SALUD
# ============================================================================

class ProfesionalSaludAdmin(admin.ModelAdmin):
    """Configuración del panel de administración para ProfesionalSalud."""

    list_display = ('get_full_name', 'especialidad', 'numero_registro_prof', 'get_email')
    search_fields = ('user_account__first_name', 'user_account__last_name', 'numero_registro_prof', 'especialidad__nombre_especialidad')
    list_filter = ('especialidad',)
    raw_id_fields = ('user_account', 'especialidad')

    @admin.display(description='Nombre Completo')
    def get_full_name(self, obj):
        """Retorna el nombre completo del profesional desde su cuenta de usuario."""
        return obj.user_account.get_full_name() or obj.user_account.username if obj.user_account else "N/A"

    @admin.display(description='Correo Electrónico')
    def get_email(self, obj):
        """Retorna el correo electrónico del profesional desde su cuenta de usuario."""
        return obj.user_account.email if obj.user_account else "N/A"


# ============================================================================
# ADMINISTRACIÓN DE ASESORES DE SERVICIO
# ============================================================================

class AsesorServicioAdmin(admin.ModelAdmin):
    """Configuración del panel de administración para AsesorServicio."""

    list_display = ('get_full_name', 'get_email')
    search_fields = ('user_account__first_name', 'user_account__last_name', 'user_account__email')
    raw_id_fields = ('user_account',)

    @admin.display(description='Nombre Completo')
    def get_full_name(self, obj):
        """Retorna el nombre completo del asesor desde su cuenta de usuario."""
        return obj.user_account.get_full_name() or obj.user_account.username if obj.user_account else "N/A"

    @admin.display(description='Correo Electrónico')
    def get_email(self, obj):
        """Retorna el correo electrónico del asesor desde su cuenta de usuario."""
        return obj.user_account.email if obj.user_account else "N/A"


# ============================================================================
# ADMINISTRACIÓN DE PLANTILLAS DE HORARIO
# ============================================================================

class PlantillaHorarioMedicoAdmin(admin.ModelAdmin):
    """Configuración del panel de administración para PlantillaHorarioMedico."""

    list_display = ('profesional', 'get_dia_semana_display', 'hora_inicio_bloque', 'hora_fin_bloque')
    list_filter = ('profesional', 'dia_semana')
    search_fields = ('profesional__user_account__first_name', 'profesional__user_account__last_name')

    @admin.display(description='Día de la Semana')
    def get_dia_semana_display(self, obj):
        """Retorna el nombre del día de la semana."""
        return obj.get_dia_semana_display()


# ============================================================================
# ADMINISTRACIÓN DE CITAS
# ============================================================================

class CitaAdmin(admin.ModelAdmin):
    """Configuración del panel de administración para Cita."""

    list_display = ('paciente', 'profesional', 'get_fecha_hora_inicio_local', 'get_fecha_hora_fin_local', 'estado_cita', 'asesor_que_agenda')
    list_filter = ('estado_cita', 'profesional', 'fecha_hora_inicio_cita')
    search_fields = (
        'paciente__user_account__first_name', 'paciente__user_account__last_name', 'paciente__numero_documento',
        'profesional__user_account__first_name', 'profesional__user_account__last_name'
    )
    list_select_related = ('paciente__user_account', 'profesional__user_account', 'profesional__especialidad', 'asesor_que_agenda__user_account')
    date_hierarchy = 'fecha_hora_inicio_cita'
    ordering = ('-fecha_hora_inicio_cita',)

    @admin.display(description='Inicio Cita (Local)', ordering='fecha_hora_inicio_cita')
    def get_fecha_hora_inicio_local(self, obj):
        """Retorna la fecha y hora de inicio de la cita en zona horaria local."""
        return timezone.localtime(obj.fecha_hora_inicio_cita).strftime('%d/%m/%Y %H:%M:%S') if obj.fecha_hora_inicio_cita else None

    @admin.display(description='Fin Cita (Local)', ordering='fecha_hora_fin_cita')
    def get_fecha_hora_fin_local(self, obj):
        """Retorna la fecha y hora de fin de la cita en zona horaria local."""
        return timezone.localtime(obj.fecha_hora_fin_cita).strftime('%d/%m/%Y %H:%M:%S') if obj.fecha_hora_fin_cita else None


# ============================================================================
# REGISTRO DE MODELOS
# ============================================================================

admin.site.register(Especialidad)
admin.site.register(Paciente, PacienteAdmin)
admin.site.register(ProfesionalSalud, ProfesionalSaludAdmin)
admin.site.register(PlantillaHorarioMedico, PlantillaHorarioMedicoAdmin)
admin.site.register(AsesorServicio, AsesorServicioAdmin)
admin.site.register(Cita, CitaAdmin)