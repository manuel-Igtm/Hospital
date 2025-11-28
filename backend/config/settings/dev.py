"""
Development settings for Hospital Backend.
These settings are used during local development.
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Database - SQLite for quick local development (PostgreSQL preferred)
DATABASES = {"default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3")}

# Additional dev apps
INSTALLED_APPS += [
    "django_extensions",
    "debug_toolbar",
]

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

# Debug toolbar
INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Allow all CORS in development
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework - browsable API in dev with session auth for browser login
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [
    "rest_framework.authentication.SessionAuthentication",
    "rest_framework_simplejwt.authentication.JWTAuthentication",
]

# Email backend - console for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Celery - eager execution in development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Cache - use local memory cache in development (no Redis required)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Logging - verbose in development
LOGGING["root"]["level"] = "DEBUG"

# Disable some security features for easier development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Login redirects for browsable API
LOGIN_REDIRECT_URL = "/api/v1/"
LOGOUT_REDIRECT_URL = "/api-auth/login/"

print("🏥 Hospital Backend - Development Mode")
print(f"📊 Database: {DATABASES['default']['ENGINE']}")
print(f"🔧 Debug Mode: {DEBUG}")
