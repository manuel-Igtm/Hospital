"""
Production settings for Hospital Backend.
These settings prioritize security, performance, and reliability.
"""

from .base import *

DEBUG = False

# Security - enforce HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database - PostgreSQL required in production
DATABASES = {
    'default': env.db('DATABASE_URL')
}

# Ensure PostgreSQL is being used
if 'postgresql' not in DATABASES['default']['ENGINE']:
    raise ValueError("Production requires PostgreSQL. Set DATABASE_URL to a PostgreSQL connection string.")

# Connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
}

# Caching - Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
        },
        'KEY_PREFIX': 'hospital',
    }
}

# Session backend - Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Static files - use WhiteNoise or CDN
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Logging - JSON format for production
LOGGING['formatters']['production'] = {
    'format': '%(asctime)s [%(process)d] [%(levelname)s] %(name)s: %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
}
LOGGING['handlers']['console']['formatter'] = 'production'
LOGGING['root']['level'] = 'INFO'

# Email configuration (configure with actual SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@hospital.example.com')

# Sentry error tracking (optional)
SENTRY_DSN = env('SENTRY_DSN', default=None)
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production',
    )

# Admin security
ADMIN_URL = env('ADMIN_URL', default='admin/')

# CORS - strict in production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')

# PII encryption key - REQUIRED in production
if not HOSPITAL_SETTINGS.get('PII_ENCRYPTION_KEY'):
    raise ValueError("PII_ENCRYPTION_KEY must be set in production for encrypting patient data")

# C modules - enabled in production for performance
HOSPITAL_SETTINGS['ENABLE_C_MODULES'] = True

print("🏥 Hospital Backend - Production Mode")
print(f"🔒 Security: Enhanced")
print(f"📊 Database: PostgreSQL")
print(f"⚡ Cache: Redis")
