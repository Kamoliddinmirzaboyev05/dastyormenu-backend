"""Development settings."""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# CORS for local frontends (admin + client dev servers).
# corsheaders is already in base INSTALLED_APPS/MIDDLEWARE — don't re-add.
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://localhost:5174',
    'http://127.0.0.1:5173',
]
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:5173',
    'http://localhost:5174',
    'http://localhost:3000',
]

# Refresh cookie over plain http in dev.
AUTH_COOKIE_SECURE = False
AUTH_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'

# In-console email + verbose logging convenience can be added here as needed.
