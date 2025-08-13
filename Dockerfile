# syntax=docker/dockerfile:1.6

############################
# Stage 1 — Build (deps)
############################
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Build deps for compiling wheels (psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libmagic1 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Use Docker layer caching: copy requirements first
COPY requirements.txt .

# Create a dedicated virtualenv for dependencies
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install -r requirements.txt


############################
# Stage 2 — Runtime
############################
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE="lcr.settings"  # adjust if your settings module differs

# Only runtime libs here (no compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libmagic1 \
  && rm -rf /var/lib/apt/lists/*

# Non-root user + folders
RUN useradd -m -r -s /bin/bash appuser \
 && mkdir -p /app /static \
 && chown -R appuser:appuser /app /static

WORKDIR /app

# Bring the virtualenv from the builder
COPY --from=builder /opt/venv /opt/venv

# Copy project code
COPY --chown=appuser:appuser . .

# Entrypoint script
COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

EXPOSE 8000

# Optional: simple TCP healthcheck on 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD python - <<'PY'\nimport socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',8000)); s.close()\nPY

# Start the app (migrations + collectstatic are in entrypoint)
CMD ["/entrypoint.sh"]
