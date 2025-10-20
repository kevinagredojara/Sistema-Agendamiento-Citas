#!/usr/bin/env bash
# Salir inmediatamente si un comando falla
set -o errexit

echo "Running collectstatic..."
python manage.py collectstatic --no-input

echo "Applying database migrations..."
python manage.py migrate

echo "Starting Gunicorn server..."
gunicorn core_project.wsgi