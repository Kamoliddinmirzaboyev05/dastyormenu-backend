"""Production settings."""
import os
import sys
from .base import *

DEBUG = os.getenv('DEBUG', 'False') == 'True'

# --- Fail closed on insecure config -------------------------------------------
if not DEBUG:
    if SECRET_KEY == 'django-insecure-change-this-in-production' or not SECRET_KEY:
        raise RuntimeError(
            'SECRET_KEY must be set to a strong value in production. '
            'Generate one with scripts/generate_secret_key.py.'
        )

# ALLOWED_HOSTS — must be explicit in production.
allowed_hosts = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts.split(',') if h.strip()]
if not ALLOWED_HOSTS and not DEBUG:
    raise RuntimeError('ALLOWED_HOSTS must be set in production (comma-separated domains).')

# CORS — explicit allowlist only. NEVER allow-all with credentials.
cors_origins = [o.strip() for o in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()]
CORS_ALLOWED_ORIGINS = cors_origins
CORS_ALLOW_CREDENTIALS = True
if not CORS_ALLOWED_ORIGINS and not DEBUG:
    # Don't crash, but warn loudly — frontends won't be able to call the API.
    print('WARNING: CORS_ALLOWED_ORIGINS is empty; no browser origin can call the API.', file=sys.stderr)

# CSRF trusted origins — derive from CORS origins if not set explicitly.
csrf_origins = [o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]
CSRF_TRUSTED_ORIGINS = csrf_origins or list(CORS_ALLOWED_ORIGINS)

# --- Static / media -----------------------------------------------------------
# WhiteNoise for static. NOTE: media (uploads) on local disk are ephemeral on
# Railway — use ImgBB/S3 for user images (already wired via IMGBB_API_KEY / USE_S3).
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- Security -----------------------------------------------------------------
# Railway terminates TLS at the proxy; trust the forwarded header.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

# httpOnly refresh cookie hardened for cross-site SPA.
AUTH_COOKIE_SECURE = True
AUTH_COOKIE_SAMESITE = os.getenv('AUTH_COOKIE_SAMESITE', 'None')

USE_S3 = os.getenv('USE_S3', 'False') == 'True'
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY', '')
IMGBB_API_URL = 'https://api.imgbb.com/1/upload'
