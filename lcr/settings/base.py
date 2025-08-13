from pathlib import Path
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env", override=False)  # <-- add: actually read the .env


def read_secret(name, default=""):
    # Prefer *_FILE path; else raw env (supports \n-escaped values)
    file_var = os.getenv(f"{name}_FILE")
    if file_var and Path(file_var).exists():
        return Path(file_var).read_text()
    raw = os.getenv(name, default)
    return raw.replace("\\n", "\n") if raw else default

# ── Core ────────────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-not-for-prod")



DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    # "django.contrib.admin",
    # "django.contrib.auth",
    # "django.contrib.contenttypes",
    # "django.contrib.sessions",
    # "django.contrib.messages",

    "django.contrib.auth",        
    "django.contrib.contenttypes",
    "django.contrib.staticfiles", # needed for drf-spectacular-sidecar assets


    "rest_framework",
    "rest_framework_simplejwt",
    
    
    # Local apps
    "accounts",
    "rental",

    "drf_spectacular",
    "drf_spectacular_sidecar",  # ships Swagger UI assets so you don’t need internet

    "corsheaders",

    "django_filters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    # "django.contrib.auth.middleware.AuthenticationMiddleware",
    # "django.contrib.messages.middleware.MessageMiddleware",
    # "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "lcr.middleware.RequestIdMiddleware"
]

AUTH_USER_MODEL = "accounts.User"


ROOT_URLCONF = "lcr.urls"
WSGI_APPLICATION = "lcr.wsgi.application"
ASGI_APPLICATION = "lcr.asgi.application"

# ── Database ───────────────────────────────────────────────────────────────────
# Prefer DATABASE_URL (e.g. postgres://user:pass@host:5432/dbname)
# Fallback to SQLite for local/dev.
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# print(f"Using DATABASE_URL: {DATABASE_URL}")  # Debugging line to check the URL

if DATABASE_URL:
    # If you use dj-database-url, replace this section with dj_database_url.config()
    import urllib.parse as up
    up.use_decoding = True
    # Django 5+ supports DATABASES["default"] from URL via "django.db.backends.postgresql"
    # but here’s a simple manual parse for portability:
    from django.core.exceptions import ImproperlyConfigured
    try:
        import dj_database_url
    except ImportError:
        raise ImproperlyConfigured("Install dj-database-url or provide explicit DB settings.")
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ── Cache ──────────────────────────────────────────────────────────────────────
# Use Redis via CACHE_URL like: redis://:password@host:6379/1
CACHE_URL = os.getenv("CACHE_URL", "")
if CACHE_URL:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": CACHE_URL}}
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# ── Static & Media ─────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── Templates ──────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    }
]

# ── Auth / i18n / Timezone ─────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TZ", "UTC")
USE_I18N = True
USE_TZ = True

# ── Logging ────────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "[%(asctime)s] %(levelname)s %(name)s: %(message)s"},
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}




REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",  # default; open up per-view if needed
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",  # no browsable API
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",       # generic anonymous burst control
        "auth": "10/min",       # login/register scope
    },
    "EXCEPTION_HANDLER": "lcr.exceptions.custom_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS" : [
        "django_filters.rest_framework.DjangoFilterBackend"
    ]
}


# SimpleJWT (tune to your needs)
from datetime import timedelta
SIMPLE_JWT = {
    "ALGORITHM": "RS256",
    "SIGNING_KEY": read_secret("JWT_PRIVATE_KEY_PEM"),   # load full PEM via env/secret manager
    "VERIFYING_KEY": read_secret("JWT_PUBLIC_KEY_PEM"),
    "AUDIENCE": "lcr-api",
    "ISSUER": "lcr-auth",
    "JTI_CLAIM": "jti",

    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=20),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),

    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,   # add app 'rest_framework_simplejwt.token_blacklist' if you use DB blacklist

    "UPDATE_LAST_LOGIN": False,
    "LEEWAY": 45,  # seconds of clock skew tolerance

    "AUTH_HEADER_TYPES": ("Bearer",),
    "VERIFY_AUD": True,
}


# OpenAPI / Swagger
SPECTACULAR_SETTINGS = {
    "TITLE": "LCR API",
    "DESCRIPTION": "Car rental REST API (auth, fleet, bookings, payments).",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,  # keep schema separate from the UI routes
    "SCHEMA_PATH_PREFIX": r"/api",  # only include /api/* endpoints
    "COMPONENT_SPLIT_REQUEST": True,
    "SERVE_PERMISSIONS": os.getenv("SWAGGER_SERVE_PERMISSIONS", "rest_framework.permissions.AllowAny").split(","),  # lock down later for prod
    "SWAGGER_UI_DIST": "SIDECAR",  # serve assets locally
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "SECURITY": [{"BearerAuth": []}],  # default security for protected endpoints
    "SECURITY_SCHEMES": {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    },
    "SERVERS": [
        {"url": "http://localhost:8000", "description": "Local"},
        # {"url": "https://api.example.com", "description": "Prod"},
    ],
    "CACHE_TIMEOUT": 3600,
    
}


CORS_ALLOW_CREDENTIALS = False
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "https://your-frontend.example,").split(",")
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"    # or "Strict" if your UX allows
CSRF_COOKIE_HTTPONLY = False    # JS must read csrftoken to echo in header