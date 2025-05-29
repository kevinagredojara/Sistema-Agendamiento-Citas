# agendamiento/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
# NUEVAS IMPORTACIONES para validadores de contraseña 👇
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError # Para capturar errores de validate_password
# settings no es necesario importarlo aquí si validate_password los toma por defecto
# from django.conf import settings 

from django.utils.translation import gettext_lazy as _ 
from .models import Paciente, ProfesionalSalud, Especialidad, Cita 
from datetime import date
from django.utils import timezone
import re 

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
        # Eliminamos cualquier atributo HTML5 específico de PIN del widget de contraseña
        if 'password' in self.fields:
            self.fields['password'].widget.attrs.pop('pattern', None)
            self.fields['password'].widget.attrs.pop('title', None)
            self.fields['password'].widget.attrs.pop('inputmode', None)


    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", first_name):
            raise forms.ValidationError("El nombre solo debe contener letras y espacios.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", last_name):
            raise forms.ValidationError("Los apellidos solo deben contener letras y espacios.")
        return last_name

    # MÉTODO clean_password() MODIFICADO PARA USAR VALIDATORS DE DJANGO 👇
    def clean_password(self):
        password = self.cleaned_data.get('password')
        # self.instance es el objeto User que se está creando.
        # Puede no tener un pk si es un usuario nuevo, lo cual es manejado por validate_password.
        user_for_validation = self.instance 
        
        if password:
            try:
                # Llamamos a validate_password. Usará los validadores definidos en
                # settings.AUTH_PASSWORD_VALIDATORS.
                validate_password(password, user=user_for_validation)
            except DjangoValidationError as e:
                # forms.ValidationError(e.messages) mostrará los mensajes del validador directamente.
                # e.messages es una lista de mensajes de error.
                self.add_error('password', e) # Asocia los errores directamente al campo password
        return password


# ... (El resto de tus formularios: PacienteForm, UserUpdateForm, ConsultaDisponibilidadForm,
# BuscarPacientePorDocumentoForm, CitaFilterForm, ModificarCitaForm, PacienteDatosContactoForm,
# PacientePasswordChangeForm, permanecen como estaban en la última versión completa que te di) ...

# Por completitud, incluyo el resto de las clases de formulario sin cambios desde la última vez:
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
            'fecha_nacimiento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]*', 'title': 'Solo números permitidos.', 'minlength':'7', 'maxlength':'10'}),
            'telefono_contacto': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]*', 'title': 'Solo números permitidos.', 'minlength':'10', 'maxlength':'10'}),
        }

    def __init__(self, *args, **kwargs):
        super(PacienteForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get('numero_documento')
        if numero_documento:
            if not numero_documento.isdigit():
                raise forms.ValidationError("El número de documento solo debe contener números.")
            if not (7 <= len(numero_documento) <= 10):
                raise forms.ValidationError("El número de documento debe tener entre 7 y 10 dígitos.")
        return numero_documento

    def clean_telefono_contacto(self):
        telefono_contacto = self.cleaned_data.get('telefono_contacto')
        if telefono_contacto:
            if not telefono_contacto.isdigit():
                raise forms.ValidationError("El teléfono de contacto solo debe contener números.")
            if len(telefono_contacto) != 10: 
                raise forms.ValidationError("El teléfono de contacto debe tener 10 dígitos.")
        return telefono_contacto

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            if fecha_nacimiento > timezone.localdate(): 
                raise forms.ValidationError("La fecha de nacimiento no puede ser una fecha futura.")
        return fecha_nacimiento

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")
    first_name = forms.CharField(required=True, label="Nombres")
    last_name = forms.CharField(required=True, label="Apellidos")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = { 'first_name': 'Nombres', 'last_name': 'Apellidos', 'email': 'Correo Electrónico (requerido)',}

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", first_name):
            raise forms.ValidationError("El nombre solo debe contener letras y espacios.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", last_name):
            raise forms.ValidationError("Los apellidos solo deben contener letras y espacios.")
        return last_name

class ConsultaDisponibilidadForm(forms.Form):
    profesional = forms.ModelChoiceField(
        queryset=ProfesionalSalud.objects.filter(user_account__is_active=True).order_by('user_account__last_name', 'user_account__first_name'),
        label="Profesional de la Salud", empty_label="Seleccione un profesional...",
        widget=forms.Select(attrs={'class': 'form-control'}), required=True )
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha para la Consulta", required=True )

    def __init__(self, *args, **kwargs):
        super(ConsultaDisponibilidadForm, self).__init__(*args, **kwargs)
        self.fields['profesional'].label_from_instance = lambda obj: f"{obj.user_account.get_full_name()} ({obj.especialidad.nombre_especialidad})"

    def clean_fecha(self):
        fecha_seleccionada = self.cleaned_data.get('fecha')
        hoy = timezone.localdate();
        if fecha_seleccionada and fecha_seleccionada < hoy:
            raise forms.ValidationError("No se puede seleccionar una fecha pasada. Por favor, elija una fecha actual o futura.")
        return fecha_seleccionada

class BuscarPacientePorDocumentoForm(forms.Form):
    numero_documento = forms.CharField(
        label="Número de Documento del Paciente", max_length=20, required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el documento a buscar'}) )

class CitaFilterForm(forms.Form):
    fecha_desde = forms.DateField(label='Fecha Desde', required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    fecha_hasta = forms.DateField(label='Fecha Hasta', required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    profesional = forms.ModelChoiceField(
        queryset=ProfesionalSalud.objects.filter(user_account__is_active=True).order_by('user_account__last_name', 'user_account__first_name'),
        required=False, label='Profesional', empty_label="Todos los profesionales", widget=forms.Select(attrs={'class': 'form-control'}))
    ESTADOS_FILTRO_CHOICES = [('', 'Todos los estados')] + Cita.ESTADOS_CITA
    estado_cita = forms.ChoiceField(choices=ESTADOS_FILTRO_CHOICES, required=False, label='Estado de la Cita', widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(CitaFilterForm, self).__init__(*args, **kwargs)
        self.fields['profesional'].label_from_instance = lambda obj: f"{obj.user_account.get_full_name()} ({obj.especialidad.nombre_especialidad})"
    
    def clean(self):
        cleaned_data = super().clean(); fecha_desde = cleaned_data.get("fecha_desde"); fecha_hasta = cleaned_data.get("fecha_hasta")
        if fecha_desde and fecha_hasta and fecha_hasta < fecha_desde:
            self.add_error('fecha_hasta', "La fecha 'hasta' no puede ser anterior a la fecha 'desde'.")
        return cleaned_data

class ModificarCitaForm(forms.Form):
    profesional = forms.ModelChoiceField(queryset=ProfesionalSalud.objects.none(), label="Nuevo Profesional", widget=forms.Select(attrs={'class': 'form-control'}), required=True )
    fecha_cita = forms.DateField(label="Nueva Fecha para la Cita", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=True )

    def __init__(self, *args, **kwargs):
        cita_actual = kwargs.pop('cita_actual', None); super(ModificarCitaForm, self).__init__(*args, **kwargs)
        if cita_actual:
            self.fields['profesional'].queryset = ProfesionalSalud.objects.filter(
                especialidad=cita_actual.profesional.especialidad, user_account__is_active=True
            ).order_by('user_account__last_name', 'user_account__first_name')
        self.fields['profesional'].label_from_instance = lambda obj: f"{obj.user_account.get_full_name()} ({obj.especialidad.nombre_especialidad})"

    def clean_fecha_cita(self):
        fecha_seleccionada = self.cleaned_data.get('fecha_cita'); hoy = timezone.localdate() 
        if fecha_seleccionada and fecha_seleccionada < hoy:
            raise forms.ValidationError("La nueva fecha de la cita no puede ser una fecha pasada.")
        return fecha_seleccionada
        
class PacienteDatosContactoForm(forms.Form):
    email = forms.EmailField(label="Correo Electrónico", required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    telefono_contacto = forms.CharField(
        label="Teléfono de Contacto", max_length=10, required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]*', 'title': 'Ingrese solo números y exactamente 10 dígitos.'}))

    def clean_telefono_contacto(self):
        telefono = self.cleaned_data.get('telefono_contacto');
        if telefono:
            if not telefono.isdigit(): raise forms.ValidationError("El teléfono solo debe contener números.")
            if len(telefono) != 10: raise forms.ValidationError("El teléfono debe tener exactamente 10 dígitos.")
        return telefono

class PacientePasswordChangeForm(PasswordChangeForm): # Formulario para cuando el PACIENTE cambia su PIN
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['new_password1', 'new_password2']:
            self.fields[field_name].widget = forms.PasswordInput(attrs={
                'class': 'form-control', 'pattern': '[0-9]{4}',
                'title': 'Su nuevo PIN debe ser numérico y de 4 dígitos.',
                'inputmode': 'numeric', 'autocomplete': 'new-password' 
            })
            self.fields[field_name].help_text = ("Su nuevo PIN debe ser numérico de 4 dígitos, no todos iguales y no secuencial.")
        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['old_password'].label = "PIN Actual"
        self.fields['new_password1'].label = "Nuevo PIN"
        self.fields['new_password2'].label = "Confirmación del Nuevo PIN"

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password: 
            if not password.isdigit(): raise forms.ValidationError("El nuevo PIN debe ser completamente numérico.", code='pin_not_numeric')
            if len(password) != 4: raise forms.ValidationError("El nuevo PIN debe tener exactamente 4 dígitos.", code='pin_invalid_length')
            if len(set(password)) == 1: raise forms.ValidationError("El nuevo PIN no debe tener todos los dígitos iguales (ej. 1111).", code='pin_digits_repeated')
            digits = [int(d) for d in password] 
            is_ascending = all(digits[i] + 1 == digits[i+1] for i in range(len(digits)-1))
            is_descending = all(digits[i] - 1 == digits[i+1] for i in range(len(digits)-1))
            if is_ascending: raise forms.ValidationError("El nuevo PIN no debe ser una secuencia numérica ascendente (ej. 1234).", code='pin_ascending_sequential')
            if is_descending: raise forms.ValidationError("El nuevo PIN no debe ser una secuencia numérica descendente (ej. 4321).", code='pin_descending_sequential')
        return password

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")
        if new_password1 and new_password2: 
            if new_password1 != new_password2:
                raise forms.ValidationError( self.error_messages['password_mismatch'], code='password_mismatch')
        return new_password2