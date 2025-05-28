# agendamiento/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Paciente, ProfesionalSalud, Especialidad, Cita 
from datetime import date # Asegúrate que date esté importado
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
            if field_name == 'password':
                field.widget.attrs['pattern'] = '[0-9]{4}'
                field.widget.attrs['title'] = 'La contraseña debe ser un PIN numérico de 4 dígitos.'
                field.widget.attrs['inputmode'] = 'numeric'

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

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if not password.isdigit():
                raise forms.ValidationError("La contraseña debe ser completamente numérica.")
            if len(password) != 4:
                raise forms.ValidationError("La contraseña debe tener exactamente 4 dígitos.")
            if len(set(password)) == 1:
                raise forms.ValidationError("La contraseña no debe tener todos los dígitos iguales (ej. 1111).")
            digits = [int(d) for d in password]
            is_ascending = all(digits[i] + 1 == digits[i+1] for i in range(len(digits)-1))
            is_descending = all(digits[i] - 1 == digits[i+1] for i in range(len(digits)-1))
            if is_ascending:
                raise forms.ValidationError("La contraseña no debe ser una secuencia numérica ascendente (ej. 1234).")
            if is_descending:
                raise forms.ValidationError("La contraseña no debe ser una secuencia numérica descendente (ej. 4321).")
        return password

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
            # Especificar el formato que el widget espera para el valor inicial y para parsear
            'fecha_nacimiento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]*', 'title': 'Solo números permitidos.', 'minlength':'7', 'maxlength':'10'}),
            'telefono_contacto': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]*', 'title': 'Solo números permitidos.', 'minlength':'10', 'maxlength':'10'}),
        }

    def __init__(self, *args, **kwargs):
        super(PacienteForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'): # Aplicar solo si no se especificó en widgets
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

    # VALIDACIÓN AÑADIDA PARA FECHA DE NACIMIENTO 👇
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            # Verificar que la fecha de nacimiento no sea posterior al día de hoy
            if fecha_nacimiento > timezone.localdate(): # timezone.localdate() da la fecha actual
                raise forms.ValidationError("La fecha de nacimiento no puede ser una fecha futura.")
            # Opcional: Verificar que no sea demasiado antigua (ej. más de 120 años)
            # if fecha_nacimiento < (timezone.localdate() - timedelta(days=120*365)):
            #     raise forms.ValidationError("Fecha de nacimiento no válida (demasiado antigua).")
        return fecha_nacimiento

class UserUpdateForm(forms.ModelForm):
    # ... (UserUpdateForm como estaba, incluyendo sus validaciones de nombre/apellido) ...
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
    # ... (sin cambios) ...
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
    # ... (sin cambios) ...
    numero_documento = forms.CharField(
        label="Número de Documento del Paciente",
        max_length=20, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el documento a buscar'})
    )

class CitaFilterForm(forms.Form):
    # ... (sin cambios) ...
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
    # ... (sin cambios) ...
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
        
class PacienteDatosContactoForm(forms.Form):
    # ... (sin cambios aquí, ya tenía validación de teléfono) ...
    email = forms.EmailField(
        label="Correo Electrónico", 
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    telefono_contacto = forms.CharField(
        label="Teléfono de Contacto", 
        max_length=10, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]*', 'title': 'Ingrese solo números y exactamente 10 dígitos.'})
    )

    def clean_telefono_contacto(self):
        telefono = self.cleaned_data.get('telefono_contacto')
        if telefono:
            if not telefono.isdigit():
                raise forms.ValidationError("El teléfono solo debe contener números.")
            if len(telefono) != 10: 
                raise forms.ValidationError("El teléfono debe tener exactamente 10 dígitos.")
        return telefono