"""
Formularios del Sistema de Agendamiento de Citas.

Define los formularios para gestión de usuarios, pacientes, citas y cambio de contraseñas.
Incluye validaciones personalizadas para datos de contacto, documentos y fechas.
"""
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import re

from .models import Paciente, ProfesionalSalud, Cita

# ============================================================================
# FORMULARIOS DE USUARIO Y AUTENTICACIÓN
# ============================================================================

class UserForm(forms.ModelForm):
    """
    Formulario para creación de usuarios del sistema.
    
    Incluye validación de contraseñas usando los validadores configurados en settings.py.
    Valida nombres y apellidos para que contengan solo letras y espacios.
    """

    password = forms.CharField(widget=forms.PasswordInput(), label="Contraseña")
    email = forms.EmailField(required=True, label="Correo Electrónico")
    first_name = forms.CharField(required=True, label="Nombres")
    last_name = forms.CharField(required=True, label="Apellidos")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        labels = {'username': 'Nombre de Usuario (para login)'}
        help_texts = {'username': None}

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # Eliminar atributos HTML5 específicos de PIN del widget de contraseña
        if 'password' in self.fields:
            self.fields['password'].widget.attrs.pop('pattern', None)
            self.fields['password'].widget.attrs.pop('title', None)
            self.fields['password'].widget.attrs.pop('inputmode', None)

    def clean_first_name(self):
        """Valida que el nombre contenga solo letras y espacios."""
        first_name = self.cleaned_data.get('first_name')
        if first_name and not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", first_name):
            raise forms.ValidationError("El nombre solo debe contener letras y espacios.")
        return first_name

    def clean_last_name(self):
        """Valida que los apellidos contengan solo letras y espacios."""
        last_name = self.cleaned_data.get('last_name')
        if last_name and not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", last_name):
            raise forms.ValidationError("Los apellidos solo deben contener letras y espacios.")
        return last_name

    def clean_password(self):
        """
        Valida la contraseña usando los validadores configurados en settings.AUTH_PASSWORD_VALIDATORS.
        
        Los validadores aplicados incluyen: longitud mínima, contraseñas comunes y contraseñas numéricas.
        """
        password = self.cleaned_data.get('password')
        
        if password:
            try:
                validate_password(password, user=self.instance)
            except DjangoValidationError as e:
                self.add_error('password', e)
        
        return password


class UserUpdateForm(forms.ModelForm):
    """
    Formulario para actualización de datos de usuario.
    
    Permite modificar nombres, apellidos y correo electrónico.
    """

    email = forms.EmailField(required=True, label="Correo Electrónico")
    first_name = forms.CharField(required=True, label="Nombres")
    last_name = forms.CharField(required=True, label="Apellidos")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico (requerido)'
        }

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
    def clean_first_name(self):
        """Valida que el nombre contenga solo letras y espacios."""
        first_name = self.cleaned_data.get('first_name')
        if first_name and not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", first_name):
            raise forms.ValidationError("El nombre solo debe contener letras y espacios.")
        return first_name

    def clean_last_name(self):
        """Valida que los apellidos contengan solo letras y espacios."""
        last_name = self.cleaned_data.get('last_name')
        if last_name and not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", last_name):
            raise forms.ValidationError("Los apellidos solo deben contener letras y espacios.")
        return last_name


# ============================================================================
# FORMULARIOS DE PACIENTES
# ============================================================================

class PacienteForm(forms.ModelForm):
    """
    Formulario para registro y actualización de datos de pacientes.
    
    Valida:
    - Número de documento: 7-10 dígitos numéricos
    - Teléfono: 10 dígitos numéricos
    - Fecha de nacimiento: entre 1900 y fecha actual
    """

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
            'fecha_nacimiento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]*', 'title': 'Solo números permitidos.', 'minlength': '7', 'maxlength': '10'}),
            'telefono_contacto': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]*', 'title': 'Solo números permitidos.', 'minlength': '10', 'maxlength': '10'}),
        }

    def __init__(self, *args, **kwargs):
        super(PacienteForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'

    def clean_numero_documento(self):
        """Valida que el número de documento tenga entre 7 y 10 dígitos numéricos."""
        numero_documento = self.cleaned_data.get('numero_documento')
        if numero_documento:
            if not numero_documento.isdigit():
                raise forms.ValidationError("El número de documento solo debe contener números.")
            if not (7 <= len(numero_documento) <= 10):
                raise forms.ValidationError("El número de documento debe tener entre 7 y 10 dígitos.")
        return numero_documento

    def clean_telefono_contacto(self):
        """Valida que el teléfono tenga exactamente 10 dígitos numéricos."""
        telefono_contacto = self.cleaned_data.get('telefono_contacto')
        if telefono_contacto:
            if not telefono_contacto.isdigit():
                raise forms.ValidationError("El teléfono de contacto solo debe contener números.")
            if len(telefono_contacto) != 10:
                raise forms.ValidationError("El teléfono de contacto debe tener 10 dígitos.")
        return telefono_contacto

    def clean_fecha_nacimiento(self):
        """Valida que la fecha de nacimiento esté entre 1900 y la fecha actual."""
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            if fecha_nacimiento > timezone.localdate():
                raise forms.ValidationError("La fecha de nacimiento no puede ser una fecha futura.")
            if fecha_nacimiento.year < 1900:
                raise forms.ValidationError("La fecha de nacimiento no puede ser anterior al año 1900.")
        return fecha_nacimiento


class PacienteDatosContactoForm(forms.Form):
    """
    Formulario para actualización de datos de contacto del paciente.
    
    Permite modificar correo electrónico y teléfono de contacto.
    """

    email = forms.EmailField(
        label="Correo Electrónico",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    telefono_contacto = forms.CharField(
        label="Teléfono de Contacto",
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '[0-9]*',
            'title': 'Ingrese solo números y exactamente 10 dígitos.'
        })
    )

    def clean_telefono_contacto(self):
        """Valida que el teléfono tenga exactamente 10 dígitos numéricos."""
        telefono = self.cleaned_data.get('telefono_contacto')
        if telefono:
            if not telefono.isdigit():
                raise forms.ValidationError("El teléfono solo debe contener números.")
            if len(telefono) != 10:
                raise forms.ValidationError("El teléfono debe tener exactamente 10 dígitos.")
        return telefono


class PacientePasswordChangeForm(PasswordChangeForm):
    """
    Formulario para cambio de PIN de paciente.
    
    Valida que el nuevo PIN:
    - Sea numérico de 4 dígitos
    - No tenga todos los dígitos iguales (ej. 1111)
    - No sea secuencia ascendente (ej. 1234)
    - No sea secuencia descendente (ej. 4321)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name in ['new_password1', 'new_password2']:
            self.fields[field_name].widget = forms.PasswordInput(attrs={
                'class': 'form-control',
                'pattern': '[0-9]{4}',
                'title': 'Su nuevo PIN debe ser numérico y de 4 dígitos.',
                'inputmode': 'numeric',
                'autocomplete': 'new-password'
            })
            self.fields[field_name].help_text = "Su nuevo PIN debe ser numérico de 4 dígitos, no todos iguales y no secuencial."
        
        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['old_password'].label = "PIN Actual"
        self.fields['new_password1'].label = "Nuevo PIN"
        self.fields['new_password2'].label = "Confirmación del Nuevo PIN"

    def clean_new_password1(self):
        """
        Valida el nuevo PIN de 4 dígitos.
        
        Rechaza PINs con todos los dígitos iguales o secuenciales.
        """
        password = self.cleaned_data.get('new_password1')
        
        if password:
            if not password.isdigit():
                raise forms.ValidationError("El nuevo PIN debe ser completamente numérico.", code='pin_not_numeric')
            if len(password) != 4:
                raise forms.ValidationError("El nuevo PIN debe tener exactamente 4 dígitos.", code='pin_invalid_length')
            if len(set(password)) == 1:
                raise forms.ValidationError("El nuevo PIN no debe tener todos los dígitos iguales (ej. 1111).", code='pin_digits_repeated')
            
            digits = [int(d) for d in password]
            is_ascending = all(digits[i] + 1 == digits[i + 1] for i in range(len(digits) - 1))
            is_descending = all(digits[i] - 1 == digits[i + 1] for i in range(len(digits) - 1))
            
            if is_ascending:
                raise forms.ValidationError("El nuevo PIN no debe ser una secuencia numérica ascendente (ej. 1234).", code='pin_ascending_sequential')
            if is_descending:
                raise forms.ValidationError("El nuevo PIN no debe ser una secuencia numérica descendente (ej. 4321).", code='pin_descending_sequential')
        
        return password

    def clean_new_password2(self):
        """Valida que ambos PINs coincidan."""
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError(self.error_messages['password_mismatch'], code='password_mismatch')
        
        return new_password2
    

# ============================================================================
# FORMULARIOS DE CITAS Y DISPONIBILIDAD
# ============================================================================

class ConsultaDisponibilidadForm(forms.Form):
    """
    Formulario para consultar disponibilidad de profesionales.
    
    Permite seleccionar un profesional activo y una fecha para verificar horarios disponibles.
    """

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
        """Valida que la fecha seleccionada no sea pasada."""
        fecha_seleccionada = self.cleaned_data.get('fecha')
        hoy = timezone.localdate()
        
        if fecha_seleccionada and fecha_seleccionada < hoy:
            raise forms.ValidationError("No se puede seleccionar una fecha pasada. Por favor, elija una fecha actual o futura.")
        
        return fecha_seleccionada


class BuscarPacientePorDocumentoForm(forms.Form):
    """Formulario para búsqueda de pacientes por número de documento."""

    numero_documento = forms.CharField(
        label="Número de Documento del Paciente",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el documento a buscar'})
    )


class CitaFilterForm(forms.Form):
    """
    Formulario para filtrado de citas.
    
    Permite filtrar citas por rango de fechas, profesional y estado.
    """

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
        """Valida que la fecha hasta no sea anterior a la fecha desde."""
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get("fecha_desde")
        fecha_hasta = cleaned_data.get("fecha_hasta")
        
        if fecha_desde and fecha_hasta and fecha_hasta < fecha_desde:
            self.add_error('fecha_hasta', "La fecha 'hasta' no puede ser anterior a la fecha 'desde'.")
        
        return cleaned_data


class ModificarCitaForm(forms.Form):
    """
    Formulario para modificación de citas existentes.
    
    Permite cambiar el profesional (dentro de la misma especialidad) y la fecha de la cita.
    """

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
        """Valida que la nueva fecha de la cita no sea pasada."""
        fecha_seleccionada = self.cleaned_data.get('fecha_cita')
        hoy = timezone.localdate()
        
        if fecha_seleccionada and fecha_seleccionada < hoy:
            raise forms.ValidationError("La nueva fecha de la cita no puede ser una fecha pasada.")
        
        return fecha_seleccionada