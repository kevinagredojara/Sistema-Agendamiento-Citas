# agendamiento/forms.py
from django import forms
from django.contrib.auth.models import User
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
        required=True
    )
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha para la Consulta",
        required=True
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
        empty_label="Todos los profesionales",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    ESTADOS_FILTRO_CHOICES = [('', 'Todos los estados')] + Cita.ESTADOS_CITA
    estado_cita = forms.ChoiceField(
        choices=ESTADOS_FILTRO_CHOICES,
        required=False,
        label='Estado de la Cita',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(CitaFilterForm, self).__init__(*args, **kwargs)
        self.fields['profesional'].label_from_instance = lambda obj: f"{obj.user_account.get_full_name()} ({obj.especialidad.nombre_especialidad})"
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get("fecha_desde")
        fecha_hasta = cleaned_data.get("fecha_hasta")

        if fecha_desde and fecha_hasta and fecha_hasta < fecha_desde:
            self.add_error('fecha_hasta', "La fecha 'hasta' no puede ser anterior a la fecha 'desde'.")
        return cleaned_data

class ModificarCitaForm(forms.Form):
    profesional = forms.ModelChoiceField(
        queryset=ProfesionalSalud.objects.none(), 
        label="Nuevo Profesional",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True 
    )
    fecha_cita = forms.DateField(
        label="Nueva Fecha para la Cita",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True 
    )

    def __init__(self, *args, **kwargs):
        cita_actual = kwargs.pop('cita_actual', None) 
        super(ModificarCitaForm, self).__init__(*args, **kwargs)
        
        if cita_actual:
            self.fields['profesional'].queryset = ProfesionalSalud.objects.filter(
                especialidad=cita_actual.profesional.especialidad,
                user_account__is_active=True
            ).order_by('user_account__last_name', 'user_account__first_name')
        self.fields['profesional'].label_from_instance = lambda obj: f"{obj.user_account.get_full_name()} ({obj.especialidad.nombre_especialidad})"

    def clean_fecha_cita(self):
        fecha_seleccionada = self.cleaned_data.get('fecha_cita')
        hoy = timezone.localdate() 
        if fecha_seleccionada and fecha_seleccionada < hoy:
            raise forms.ValidationError("La nueva fecha de la cita no puede ser una fecha pasada.")
        return fecha_seleccionada

# FORMULARIO PARA ACTUALIZAR DATOS DE CONTACTO DEL PACIENTE (HU-PAC-002) 👇
class PacienteDatosContactoForm(forms.Form):
    email = forms.EmailField(
        label="Correo Electrónico", 
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    telefono_contacto = forms.CharField(
        label="Teléfono de Contacto", 
        max_length=20, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]+', 'title': 'Ingrese solo números para el teléfono.'}) # Añadida validación básica HTML5
    )

    # Podríamos añadir validaciones personalizadas clean_email o clean_telefono_contacto si es necesario