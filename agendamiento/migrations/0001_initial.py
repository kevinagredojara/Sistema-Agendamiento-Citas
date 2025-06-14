# Generated by Django 5.2.1 on 2025-05-23 04:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Especialidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_especialidad', models.CharField(max_length=100, unique=True, verbose_name='Nombre de la Especialidad')),
                ('duracion_consulta_minutos', models.PositiveIntegerField(verbose_name='Duración Estándar de Consulta (minutos)')),
                ('activa', models.BooleanField(default=True, verbose_name='¿Está activa?')),
            ],
            options={
                'verbose_name': 'Especialidad Médica',
                'verbose_name_plural': 'Especialidades Médicas',
                'ordering': ['nombre_especialidad'],
            },
        ),
        migrations.CreateModel(
            name='AsesorServicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='asesor_perfil', to=settings.AUTH_USER_MODEL, verbose_name='Cuenta de Usuario')),
            ],
            options={
                'verbose_name': 'Asesor de Servicio',
                'verbose_name_plural': 'Asesores de Servicio',
                'ordering': ['user_account__last_name', 'user_account__first_name'],
            },
        ),
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_documento', models.CharField(choices=[('CC', 'Cédula de Ciudadanía'), ('TI', 'Tarjeta de Identidad'), ('RC', 'Registro Civil'), ('CE', 'Cédula de Extranjería'), ('PA', 'Pasaporte')], max_length=30, verbose_name='Tipo de Documento')),
                ('numero_documento', models.CharField(max_length=20, unique=True, verbose_name='Número de Documento')),
                ('fecha_nacimiento', models.DateField(verbose_name='Fecha de Nacimiento')),
                ('telefono_contacto', models.CharField(max_length=20, verbose_name='Teléfono de Contacto')),
                ('user_account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='paciente_perfil', to=settings.AUTH_USER_MODEL, verbose_name='Cuenta de Usuario')),
            ],
            options={
                'verbose_name': 'Paciente',
                'verbose_name_plural': 'Pacientes',
                'ordering': ['user_account__last_name', 'user_account__first_name'],
            },
        ),
        migrations.CreateModel(
            name='ProfesionalSalud',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_registro_prof', models.CharField(max_length=30, verbose_name='Número de Registro Profesional')),
                ('telefono_contacto_prof', models.CharField(blank=True, max_length=20, null=True, verbose_name='Teléfono de Contacto Profesional')),
                ('especialidad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='profesionales', to='agendamiento.especialidad', verbose_name='Especialidad')),
                ('user_account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profesional_perfil', to=settings.AUTH_USER_MODEL, verbose_name='Cuenta de Usuario')),
            ],
            options={
                'verbose_name': 'Profesional de la Salud',
                'verbose_name_plural': 'Profesionales de la Salud',
                'ordering': ['user_account__last_name', 'user_account__first_name'],
            },
        ),
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora_inicio_cita', models.DateTimeField(verbose_name='Fecha y Hora de Inicio de Cita')),
                ('fecha_hora_fin_cita', models.DateTimeField(verbose_name='Fecha y Hora de Fin de Cita')),
                ('estado_cita', models.CharField(choices=[('Programada', 'Programada'), ('Cancelada', 'Cancelada'), ('Realizada', 'Realizada'), ('No_Asistio', 'No Asistió')], default='Programada', max_length=25, verbose_name='Estado de la Cita')),
                ('asesor_que_agenda', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='citas_agendadas', to='agendamiento.asesorservicio', verbose_name='Asesor que Agenda')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='citas', to='agendamiento.paciente', verbose_name='Paciente')),
                ('profesional', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='citas_atendidas', to='agendamiento.profesionalsalud', verbose_name='Profesional de la Salud')),
            ],
            options={
                'verbose_name': 'Cita Médica',
                'verbose_name_plural': 'Citas Médicas',
                'ordering': ['fecha_hora_inicio_cita', 'profesional'],
            },
        ),
        migrations.CreateModel(
            name='PlantillaHorarioMedico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_semana', models.IntegerField(choices=[(0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')], verbose_name='Día de la Semana')),
                ('hora_inicio_bloque', models.TimeField(verbose_name='Hora de Inicio del Bloque')),
                ('hora_fin_bloque', models.TimeField(verbose_name='Hora de Fin del Bloque')),
                ('profesional', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plantillas_horario', to='agendamiento.profesionalsalud', verbose_name='Profesional de la Salud')),
            ],
            options={
                'verbose_name': 'Plantilla de Horario Médico',
                'verbose_name_plural': 'Plantillas de Horario Médico',
                'ordering': ['profesional', 'dia_semana', 'hora_inicio_bloque'],
                'unique_together': {('profesional', 'dia_semana', 'hora_inicio_bloque')},
            },
        ),
    ]
