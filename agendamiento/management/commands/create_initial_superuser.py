# agendamiento/management/commands/create_initial_superuser.py

import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crea un superusuario inicial si no existe ninguno.'

    def handle(self, *args, **options):
        # Comprueba si ya existe algún usuario en la base de datos
        if User.objects.exists():
            self.stdout.write(self.style.SUCCESS('El superusuario ya existe, no se realiza ninguna acción.'))
            return

        # Lee las credenciales desde las variables de entorno
        username = os.environ.get('ADMIN_USER')
        email = os.environ.get('ADMIN_EMAIL')
        password = os.environ.get('ADMIN_PASSWORD')

        # Valida que todas las variables necesarias estén presentes
        if not all([username, email, password]):
            self.stderr.write(self.style.ERROR(
                'Faltan las variables de entorno ADMIN_USER, ADMIN_EMAIL o ADMIN_PASSWORD.'
            ))
            return

        # Crea el superusuario de forma no interactiva
        self.stdout.write(f"Creando superusuario '{username}'...")
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superusuario '{username}' creado exitosamente."))