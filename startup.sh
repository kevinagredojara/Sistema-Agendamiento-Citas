#!/bin/bash

# Salir inmediatamente si un comando falla, para detectar errores rápidamente.
set -e

echo "Azure App Service - Iniciando script de arranque personalizado (startup.sh)..."

# El sistema de compilación Oryx de Azure generalmente ejecuta este script
# desde el directorio raíz de tu aplicación (donde está manage.py),
# que en tu caso es un directorio temporal como /tmp/8dda43f70c889f1.

echo "Aplicando migraciones de la base de datos..."
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
# La opción --clear elimina los archivos estáticos antiguos antes de copiar los nuevos.
python manage.py collectstatic --noinput --clear

echo "Iniciando servidor Gunicorn..."
# Se utiliza 'exec' para que Gunicorn reemplace el proceso del script,
# lo cual es la práctica estándar para el proceso principal de la aplicación.
# Gunicorn se enlazará al puerto que Azure App Service le proporciona a través de la variable $PORT
# y escuchará en todas las interfaces de red (0.0.0.0).
# --workers: Puedes ajustar el número de workers según el tamaño de tu App Service Plan. 2 es un buen punto de partida.
# core_project.wsgi:application : Asegúrate de que 'application' es el nombre del objeto WSGI en tu core_project/wsgi.py
# (usualmente es 'application' por defecto).
exec gunicorn core_project.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers 2 \
    --log-file - \
    --log-level info