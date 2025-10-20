#!/usr/bin/env bash
set -o errexit

echo "Running collectstatic..."
python manage.py collectstatic --no-input

echo "Applying database migrations..."
python manage.py migrate

# La línea de creación original puede quedarse, no hará nada.
echo "Creating initial superuser if it does not exist..."
python manage.py create_initial_superuser

# ----> AÑADE ESTA NUEVA LÍNEA <----
echo "Restoring superuser permissions..."
python manage.py restore_superuser

echo "Starting Gunicorn server..."
gunicorn core_project.wsgi