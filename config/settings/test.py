"""Test settings.

Runs the suite against an in-memory SQLite database so tests are hermetic and
fast, regardless of any DATABASE_URL/DB_HOST in the environment. Behaviour
under test (tenant scoping, permissions, serializers) is database-agnostic.

Run: DJANGO_SETTINGS_MODULE=config.settings.test python manage.py test
"""
from .development import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Fast, insecure hasher — fine for tests only.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Keep realtime broadcasts in-process during tests.
CHANNEL_LAYERS = {'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}}
