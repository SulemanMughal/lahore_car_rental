from .base import *

DEBUG = False

# Safer defaults for a pre-prod env
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS") else []
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Allow staging domain(s)
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "staging.example.com").split(",")

# Email: route to console or a sandbox mailbox provider
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

# Any staging-only toggles/keys (e.g. payment provider in test mode)
