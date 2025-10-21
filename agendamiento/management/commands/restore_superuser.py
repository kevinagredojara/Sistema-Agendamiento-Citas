# agendamiento/management/commands/restore_superuser.py

import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Restaura los permisos de superusuario a un usuario existente.'

    def handle(self, *args, **options):
        # Lee el nombre de usuario a restaurar desde las variables de entorno
        username_to_fix = os.environ.get('ADMIN_USER_TO_FIX')

        if not username_to_fix:
            self.stderr.write(self.style.ERROR('La variable de entorno ADMIN_USER_TO_FIX no está definida.'))
            return

        try:
            # Busca al usuario en la base de datos
            user = User.objects.get(username=username_to_fix)

            # Restaura los permisos de superadministrador
            user.is_staff = True
            user.is_superuser = True
            user.save()

            # Opcional: Elimina al usuario de todos los grupos para limpiar sus roles
            user.groups.clear()

            self.stdout.write(self.style.SUCCESS(
                f"Los permisos de superusuario para '{username_to_fix}' han sido restaurados exitosamente."
            ))

        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"El usuario '{username_to_fix}' no fue encontrado."))