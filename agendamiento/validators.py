"""
Validadores personalizados de contraseñas para el Sistema de Agendamiento.
Implementa validaciones de seguridad con mensajes en español.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import ngettext


class CustomMinimumLengthValidator:
    """
    Valida que la contraseña tenga una longitud mínima.
    Por defecto: 8 caracteres.
    """
    
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ngettext(
                    "Esta contraseña es demasiado corta. Debe contener al menos %(min_length)d carácter.",
                    "Esta contraseña es demasiado corta. Debe contener al menos %(min_length)d caracteres.",
                    self.min_length
                ),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return ngettext(
            "Su contraseña debe contener al menos %(min_length)d carácter.",
            "Su contraseña debe contener al menos %(min_length)d caracteres.",
            self.min_length
        ) % {'min_length': self.min_length}


class CustomCommonPasswordValidator:
    """
    Valida que la contraseña no sea una contraseña común o predecible.
    Utiliza la lista de contraseñas comunes de Django.
    """
    
    def validate(self, password, user=None):
        from django.contrib.auth.password_validation import CommonPasswordValidator
        
        try:
            validator = CommonPasswordValidator()
            validator.validate(password, user)
        except ValidationError:
            raise ValidationError(
                "Esta contraseña es demasiado común.",
                code='password_too_common',
            )

    def get_help_text(self):
        return "Su contraseña no puede ser una contraseña comúnmente utilizada."


class CustomNumericPasswordValidator:
    """
    Valida que la contraseña no sea completamente numérica.
    Rechaza contraseñas que solo contengan dígitos (ej: 12345678).
    """
    
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                "Esta contraseña es completamente numérica.",
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return "Su contraseña no puede ser completamente numérica."