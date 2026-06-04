#!/usr/bin/env bash
set -e

# Wait for DB? Optionally add a wait-for-it or retry logic in production

echo "Running migrations..."
python manage.py migrate --noinput || true

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn sacco_core.wsgi:application --workers ${GUNICORN_WORKERS:-3} --bind 0.0.0.0:${PORT:-8000}
