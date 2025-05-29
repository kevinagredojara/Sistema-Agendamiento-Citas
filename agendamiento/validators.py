from django.core.exceptions import ValidationError
from django.utils.translation import ngettext

class CustomMinimumLengthValidator:
    """
    Validador personalizado para longitud mínima con mensajes en español.
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
    Validador personalizado para contraseñas comunes con mensaje en español.
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
    Validador personalizado para contraseñas numéricas con mensaje en español.
    """
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                "Esta contraseña es completamente numérica.",
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return "Su contraseña no puede ser completamente numérica."