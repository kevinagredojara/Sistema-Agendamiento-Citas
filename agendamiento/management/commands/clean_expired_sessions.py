from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Limpia las sesiones expiradas del sistema para mejorar la seguridad y el rendimiento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Número de días para considerar una sesión como expirada (por defecto: 1)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué sesiones se eliminarían sin eliminarlas realmente',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        # Calcular la fecha límite
        expiry_date = timezone.now() - timedelta(days=days)
        
        # Encontrar sesiones expiradas
        expired_sessions = Session.objects.filter(expire_date__lt=expiry_date)
        count = expired_sessions.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Se eliminarían {count} sesiones expiradas desde hace más de {days} día(s)'
                )
            )
            
            if count > 0:
                self.stdout.write('\nSesiones que se eliminarían:')
                for session in expired_sessions[:10]:  # Mostrar solo las primeras 10
                    self.stdout.write(f'  - Sesión: {session.session_key[:8]}... (expiró: {session.expire_date})')
                
                if count > 10:
                    self.stdout.write(f'  ... y {count - 10} sesiones más')
        else:
            # Eliminar las sesiones expiradas
            deleted_count, _ = expired_sessions.delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Se eliminaron {deleted_count} sesiones expiradas correctamente'
                )
            )
            
            if deleted_count > 0:
                self.stdout.write(
                    f'  Estas sesiones habían expirado hace más de {days} día(s)'
                )
        
        # Mostrar estadísticas adicionales
        total_sessions = Session.objects.count()
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now()).count()
        
        self.stdout.write('\n--- Estadísticas de Sesiones ---')
        self.stdout.write(f'Total de sesiones en la base de datos: {total_sessions}')
        self.stdout.write(f'Sesiones activas: {active_sessions}')
        self.stdout.write(f'Sesiones limpiadas en esta operación: {count if not dry_run else 0}')
        
        if not dry_run and count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✓ Limpieza de sesiones completada. El sistema es más seguro y eficiente.'
                )
            )
