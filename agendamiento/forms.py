# agendamiento/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Paciente, ProfesionalSalud, Especialidad # Asegúrate de importar ProfesionalSalud y Especialidad

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
        widgets = { # Usamos widgets aquí para aplicar la clase y el tipo de input
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        super(PacienteForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'): # Aplicar solo si no tiene ya una clase
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

# NUEVO FORMULARIO PARA CONSULTAR DISPONIBILIDAD
class ConsultaDisponibilidadForm(forms.Form):
    # Campo para seleccionar un Profesional de la Salud
    # Usamos ModelChoiceField para que genere un desplegable con los profesionales existentes.
    profesional = forms.ModelChoiceField(
        queryset=ProfesionalSalud.objects.filter(user_account__is_active=True).order_by('user_account__last_name', 'user_account__first_name'),
        label="Profesional de la Salud",
        empty_label="Seleccione un profesional...", # Texto para la opción vacía
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Campo para seleccionar la fecha de la consulta
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha para la Consulta"
    )

    # Opcional: Campo para filtrar por especialidad primero (mejora futura)
    # especialidad = forms.ModelChoiceField(
    #     queryset=Especialidad.objects.filter(activa=True).order_by('nombre_especialidad'),
    #     label="Especialidad (Opcional)",
    #     required=False, # Hacemos que no sea obligatorio
    #     empty_label="Todas las especialidades...",
    #     widget=forms.Select(attrs={'class': 'form-control'})
    # )

    def __init__(self, *args, **kwargs):
        super(ConsultaDisponibilidadForm, self).__init__(*args, **kwargs)
        # Podríamos personalizar cómo se muestran los profesionales en el desplegable
        # si el __str__ del modelo ProfesionalSalud no es suficiente.
        # Por ejemplo, para mostrar "Apellido, Nombre (Especialidad)":
        self.fields['profesional'].label_from_instance = lambda obj: f"{obj.user_account.last_name}, {obj.user_account.first_name} ({obj.especialidad.nombre_especialidad})"