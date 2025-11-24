"""
Test settings for Hospital Backend.
Used during pytest test runs.
"""

from .base import *

DEBUG = False

# Use SQLite in-memory for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': True,
    }
}

# Password hashers - fast for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Email backend - memory for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Celery - synchronous execution in tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable throttling in tests
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []

# Simpler logging for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'CRITICAL',
    },
}

# Disable C modules in tests by default (can be overridden)
HOSPITAL_SETTINGS['ENABLE_C_MODULES'] = env.bool('ENABLE_C_MODULES', default=False)
