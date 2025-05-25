# agendamiento/admin.py
from django.contrib import admin
from .models import Especialidad, Paciente, ProfesionalSalud, PlantillaHorarioMedico, AsesorServicio, Cita
from django.utils import timezone # <--- IMPORTAR timezone

class PacienteAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'tipo_documento', 'numero_documento', 'telefono_contacto', 'get_email')
    search_fields = ('user_account__first_name', 'user_account__last_name', 'numero_documento', 'user_account__email')
    list_filter = ('tipo_documento',)

    @admin.display(description='Nombre Completo')
    def get_full_name(self, obj):
        if obj.user_account:
            return obj.user_account.get_full_name() or obj.user_account.username
        return "N/A"

    @admin.display(description='Correo Electrónico')
    def get_email(self, obj):
        if obj.user_account:
            return obj.user_account.email
        return "N/A"

class ProfesionalSaludAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'especialidad', 'numero_registro_prof', 'get_email')
    search_fields = ('user_account__first_name', 'user_account__last_name', 'numero_registro_prof', 'especialidad__nombre_especialidad')
    list_filter = ('especialidad',)
    raw_id_fields = ('user_account', 'especialidad') # Mejora la interfaz para ForeignKeys con muchos elementos

    @admin.display(description='Nombre Completo')
    def get_full_name(self, obj):
        if obj.user_account:
            return obj.user_account.get_full_name() or obj.user_account.username
        return "N/A"

    @admin.display(description='Correo Electrónico')
    def get_email(self, obj):
        if obj.user_account:
            return obj.user_account.email
        return "N/A"

class AsesorServicioAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'get_email')
    search_fields = ('user_account__first_name', 'user_account__last_name', 'user_account__email')
    raw_id_fields = ('user_account',)

    @admin.display(description='Nombre Completo')
    def get_full_name(self, obj):
        if obj.user_account:
            return obj.user_account.get_full_name() or obj.user_account.username
        return "N/A"

    @admin.display(description='Correo Electrónico')
    def get_email(self, obj):
        if obj.user_account:
            return obj.user_account.email
        return "N/A"

class PlantillaHorarioMedicoAdmin(admin.ModelAdmin):
    list_display = ('profesional', 'get_dia_semana_display', 'hora_inicio_bloque', 'hora_fin_bloque')
    list_filter = ('profesional', 'dia_semana')
    search_fields = ('profesional__user_account__first_name', 'profesional__user_account__last_name')

    @admin.display(description='Día de la Semana')
    def get_dia_semana_display(self, obj):
        return obj.get_dia_semana_display() # Llama al método del modelo que devuelve el nombre del día


class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'profesional', 'get_fecha_hora_inicio_local', 'get_fecha_hora_fin_local', 'estado_cita', 'asesor_que_agenda')
    list_filter = ('estado_cita', 'profesional', 'fecha_hora_inicio_cita')
    search_fields = (
        'paciente__user_account__first_name', 'paciente__user_account__last_name', 'paciente__numero_documento',
        'profesional__user_account__first_name', 'profesional__user_account__last_name'
    )
    list_select_related = ('paciente__user_account', 'profesional__user_account', 'profesional__especialidad', 'asesor_que_agenda__user_account') # Optimización de consultas
    date_hierarchy = 'fecha_hora_inicio_cita' # Añade navegación por jerarquía de fechas
    ordering = ('-fecha_hora_inicio_cita',) # Ordenar por fecha de inicio descendente por defecto

    @admin.display(description='Inicio Cita (Local)', ordering='fecha_hora_inicio_cita')
    def get_fecha_hora_inicio_local(self, obj):
        if obj.fecha_hora_inicio_cita:
            return timezone.localtime(obj.fecha_hora_inicio_cita).strftime('%d/%m/%Y %H:%M:%S')
        return None

    @admin.display(description='Fin Cita (Local)', ordering='fecha_hora_fin_cita')
    def get_fecha_hora_fin_local(self, obj):
        if obj.fecha_hora_fin_cita:
            return timezone.localtime(obj.fecha_hora_fin_cita).strftime('%d/%m/%Y %H:%M:%S')
        return None

# Registrar los modelos con sus clases Admin personalizadas (si las tienen)
admin.site.register(Especialidad) # Podríamos crear un EspecialidadAdmin si quisiéramos
admin.site.register(Paciente, PacienteAdmin)
admin.site.register(ProfesionalSalud, ProfesionalSaludAdmin)
admin.site.register(PlantillaHorarioMedico, PlantillaHorarioMedicoAdmin)
admin.site.register(AsesorServicio, AsesorServicioAdmin)
admin.site.register(Cita, CitaAdmin)