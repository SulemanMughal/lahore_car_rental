# env variables:


```
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
#DATABASE_URL=postgres://postgres:123456789@localhost:5432/lcr_db
DATABASE_URL=postgres://lcr:lcr@db:5432/lcr
CACHE_URL=redis://localhost:6379/1
DJANGO_LOG_LEVEL=DEBUG
DJANGO_SETTINGS_MODULE=lcr.settings.base

#JWT_PRIVATE_KEY_FILE=jwtRS256.key
#JWT_PUBLIC_KEY_FILE=jwtRS256.key.pub



# PostgreSQL settings for docker-compose
POSTGRES_DB=lcr
POSTGRES_USER=lcr
POSTGRES_PASSWORD=lcr

# JWT keys - these will be mounted as volumes in Docker
JWT_PRIVATE_KEY_FILE=/app/secrets/jwtRS256.key
JWT_PUBLIC_KEY_FILE=/app/secrets/jwtRS256.key.pub

CORS_ALLOWED_ORIGINS="https://your-frontend.example,https://another-frontend.example"


SWAGGER_SERVE_PERMISSIONS=rest_framework.permissions.AllowAny
#["rest_framework.permissions.AllowAny"]
# Swagger permissions
#SWAGGER_SERVE_PERMISSIONS=["rest_framework.permissions.AllowAny"]

# Gunicorn settings for Docker
WEB_CONCURRENCY=2
WEB_TIMEOUT=60
DJANGO_COLLECTSTATIC=1

# Timezone
TZ=UTC
```


To run this project:
```docker compose up -d --build```

to turn off this project
```docker compose down -d```