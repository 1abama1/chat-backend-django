#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
/app/docker/wait-for-it.sh db:5432 --timeout=30 --strict

echo "Waiting for Redis to be ready..."
/app/docker/wait-for-it.sh redis:6379 --timeout=10 --strict

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting server..."
export DJANGO_SETTINGS_MODULE=backend.settings
exec "$@"
