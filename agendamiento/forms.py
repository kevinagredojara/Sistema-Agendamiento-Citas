# agendamiento/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Paciente, ProfesionalSalud, Especialidad # Asegúrate de que Especialidad esté importada
from datetime import date # Para obtener la fecha actual
from django.utils import timezone # Para obtener la fecha actual con zona horaria

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
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha para la Consulta"
    )

    def __init__(self, *args, **kwargs):
        super(ConsultaDisponibilidadForm, self).__init__(*args, **kwargs)
        self.fields['profesional'].label_from_instance = lambda obj: f"{obj.user_account.last_name}, {obj.user_account.first_name} ({obj.especialidad.nombre_especialidad})"

    # --- MÉTODO DE VALIDACIÓN AÑADIDO PARA EL CAMPO 'fecha' ---
    def clean_fecha(self):
        fecha_seleccionada = self.cleaned_data.get('fecha')
        # Obtener la fecha actual en la zona horaria del proyecto para una comparación correcta
        hoy = timezone.localdate() 

        if fecha_seleccionada and fecha_seleccionada < hoy:
            raise forms.ValidationError("No se puede seleccionar una fecha pasada. Por favor, elija una fecha actual o futura.")
        return fecha_seleccionada
    # --- FIN DE MÉTODO DE VALIDACIÓN AÑADIDO ---

class SelectPacienteForm(forms.Form):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.filter(user_account__is_active=True).order_by('user_account__last_name', 'user_account__first_name'),
        label="Seleccionar Paciente",
        empty_label="Seleccione un paciente...",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(SelectPacienteForm, self).__init__(*args, **kwargs)
        self.fields['paciente'].label_from_instance = lambda obj: f"{obj.user_account.last_name}, {obj.user_account.first_name} (Doc: {obj.numero_documento})"