# agendamiento/forms.py
from django import forms
from django.contrib.auth.models import User
# Asegúrate de que ProfesionalSalud y Cita estén importados si no lo están ya
from .models import Paciente, ProfesionalSalud, Especialidad, Cita 
from datetime import date
from django.utils import timezone

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Contraseña")
    email = forms.EmailField(required=True, label="Correo Electrónico")
    first_name = forms.CharField(required=True, label="Nombres")
    last_name = forms.CharField(required=True, label="Apellidos")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        labels = {
            'username': 'Nombre de Usuario (para login)',
        }
        help_texts = {
            'username': None, 
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        exclude = ['user_account']
        labels = {
            'tipo_documento': 'Tipo de Documento',
            'numero_documento': 'Número de Documento',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'telefono_contacto': 'Teléfono de Contacto',
        }
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(PacienteForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")
    first_name = forms.CharField(required=True, label="Nombres")
    last_name = forms.CharField(required=True, label="Apellidos")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico (requerido)',
        }

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ConsultaDisponibilidadForm(forms.Form):
    profesional = forms.ModelChoiceField(
        queryset=ProfesionalSalud.objects.filter(user_account__is_active=True).order_by('user_account__last_name', 'user_account__first_name'),
        label="Profesional de la Salud",
        empty_label="Seleccione un profesional...",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True # Lo mantenemos requerido para la consulta de disponibilidad
    )
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha para la Consulta",
        required=True # Lo mantenemos requerido para la consulta de disponibilidad
    )

    def __init__(self, *args, **kwargs):
        super(ConsultaDisponibilidadForm, self).__init__(*args, **kwargs)
        self.fields['profesional'].label_from_instance = lambda obj: f"{obj.user_account.get_full_name()} ({obj.especialidad.nombre_especialidad})"

    def clean_fecha(self):
        fecha_seleccionada = self.cleaned_data.get('fecha')
        hoy = timezone.localdate() 
        if fecha_seleccionada and fecha_seleccionada < hoy:
            raise forms.ValidationError("No se puede seleccionar una fecha pasada. Por favor, elija una fecha actual o futura.")
        return fecha_seleccionada

class BuscarPacientePorDocumentoForm(forms.Form):
    numero_documento = forms.CharField(
        label="Número de Documento del Paciente",
        max_length=20, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el documento a buscar'})
    )

# NUEVO FORMULARIO PARA FILTROS DE CITAS 👇
class CitaFilterForm(forms.Form):
    fecha_desde = forms.DateField(
        label='Fecha Desde',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_hasta = forms.DateField(
        label='Fecha Hasta',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    profesional = forms.ModelChoiceField(
        queryset=ProfesionalSalud.objects.filter(user_account__is_active=True).order_by('user_account__last_name', 'user_account__first_name'),
        required=False,
        label='Profesional',
        empty_label="Todos los profesionales", # Para permitir no filtrar por profesional
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # Construimos las opciones para el estado, añadiendo una opción para "Todos"
    ESTADOS_FILTRO_CHOICES = [('', 'Todos los estados')] + Cita.ESTADOS_CITA
    estado_cita = forms.ChoiceField(
        choices=ESTADOS_FILTRO_CHOICES,
        required=False,
        label='Estado de la Cita',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(CitaFilterForm, self).__init__(*args, **kwargs)
        # Personalizar la etiqueta del profesional si es necesario, similar a ConsultaDisponibilidadForm
        self.fields['profesional'].label_from_instance = lambda obj: f"{obj.user_account.get_full_name()} ({obj.especialidad.nombre_especialidad})"
        # Podríamos añadir más personalizaciones o validaciones clean_() aquí si fueran necesarias,
        # por ejemplo, para asegurar que fecha_hasta no sea anterior a fecha_desde.
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get("fecha_desde")
        fecha_hasta = cleaned_data.get("fecha_hasta")

        if fecha_desde and fecha_hasta and fecha_hasta < fecha_desde:
            self.add_error('fecha_hasta', "La fecha 'hasta' no puede ser anterior a la fecha 'desde'.")
        return cleaned_data