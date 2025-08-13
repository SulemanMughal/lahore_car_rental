#!/usr/bin/env bash
set -euo pipefail

# Run DB migrations
python manage.py migrate --noinput

# Collect static files (toggle with env if you want to skip in dev)
: "${DJANGO_COLLECTSTATIC:=1}"
if [ "$DJANGO_COLLECTSTATIC" = "1" ]; then
  python manage.py collectstatic --noinput
fi

# Seed RBAC roles (safe to run repeatedly)
python manage.py seed_roles || true

# Start ASGI via Gunicorn + Uvicorn workers
# Tune WEB_CONCURRENCY/WEB_TIMEOUT via env
exec gunicorn lcr.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers "${WEB_CONCURRENCY:-2}" \
    --timeout "${WEB_TIMEOUT:-60}"
