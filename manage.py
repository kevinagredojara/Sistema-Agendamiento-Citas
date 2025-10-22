#!/usr/bin/env python
"""
Utilidad de línea de comandos de Django para el Sistema de Agendamiento.
Ejecuta comandos administrativos del proyecto.
"""
import os
import sys


def main():
    """Ejecuta tareas administrativas de Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Verifica que esté instalado y "
            "que hayas activado el entorno virtual correctamente."
        ) from exc
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
