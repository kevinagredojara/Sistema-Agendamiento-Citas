from django.contrib import admin
from .models import Especialidad, Paciente, ProfesionalSalud, PlantillaHorarioMedico, AsesorServicio, Cita

# Register your models here.

# Opción 1: Registro simple (muestra los modelos en el admin con su comportamiento por defecto)
admin.site.register(Especialidad)
admin.site.register(Paciente)
admin.site.register(ProfesionalSalud)
admin.site.register(PlantillaHorarioMedico)
admin.site.register(AsesorServicio)
admin.site.register(Cita)

# Más adelante, si queremos personalizar cómo se ven y se comportan estos modelos
# en el panel de administración (ej. qué columnas mostrar en las listas, añadir filtros, etc.),
# crearemos clases ModelAdmin. Por ahora, el registro simple es suficiente.
# Ejemplo de cómo sería con una clase ModelAdmin (lo haremos después si es necesario):
#
# class EspecialidadAdmin(admin.ModelAdmin):
#     list_display = ('nombre_especialidad', 'duracion_consulta_minutos', 'activa')
#     search_fields = ('nombre_especialidad',)
#
# admin.site.register(Especialidad, EspecialidadAdmin)