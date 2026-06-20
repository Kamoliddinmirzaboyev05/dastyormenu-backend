"""Shared image-upload helper with validation.

Single source of truth used by menu + organization serializers so upload
limits, timeouts and error handling stay consistent.

`store_image` is the entry point: it uploads to ImgBB when an API key is
configured, otherwise it saves to local MEDIA disk (self-hosted, persisted
via a bind-mounted volume).
"""
import base64
import os
import uuid
import requests
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import serializers

MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
UPLOAD_TIMEOUT = 15  # seconds


def _validate_image(image_file) -> None:
    """Reject oversized or unsupported uploads before storing them."""
    size = getattr(image_file, 'size', None)
    if size is not None and size > MAX_IMAGE_BYTES:
        raise serializers.ValidationError('Image too large (max 5 MB).')

    content_type = getattr(image_file, 'content_type', None)
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise serializers.ValidationError('Unsupported image type (use JPEG, PNG, GIF or WebP).')


def save_image_to_media(image_file, request=None, subdir='uploads') -> str:
    """Save an uploaded image to local MEDIA storage and return its URL.

    Returns an absolute URL when ``request`` is given (works behind a reverse
    proxy / custom domain), otherwise a root-relative MEDIA path.
    """
    _validate_image(image_file)

    ext = os.path.splitext(getattr(image_file, 'name', '') or '')[1].lower() or '.jpg'
    name = f"{subdir}/{uuid.uuid4().hex}{ext}"
    saved_path = default_storage.save(name, image_file)

    url = settings.MEDIA_URL + saved_path
    if not url.startswith(('http://', 'https://', '/')):
        url = '/' + url
    if request is not None:
        return request.build_absolute_uri(url)
    return url


def store_image(image_file, request=None, subdir='uploads') -> str:
    """Store an image: ImgBB when configured, else local MEDIA disk."""
    if settings.IMGBB_API_KEY:
        return upload_image_to_imgbb(image_file)
    return save_image_to_media(image_file, request=request, subdir=subdir)


def upload_image_to_imgbb(image_file) -> str:
    """Validate and upload an image to ImgBB, returning its URL.

    Raises serializers.ValidationError on any validation/transport failure.
    """
    if not settings.IMGBB_API_KEY:
        raise serializers.ValidationError('Image hosting is not configured (IMGBB_API_KEY).')

    size = getattr(image_file, 'size', None)
    if size is not None and size > MAX_IMAGE_BYTES:
        raise serializers.ValidationError('Image too large (max 5 MB).')

    content_type = getattr(image_file, 'content_type', None)
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise serializers.ValidationError('Unsupported image type (use JPEG, PNG, GIF or WebP).')

    try:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
        response = requests.post(
            settings.IMGBB_API_URL,
            data={'key': settings.IMGBB_API_KEY, 'image': encoded, 'name': getattr(image_file, 'name', 'upload')},
            timeout=UPLOAD_TIMEOUT,
        )
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException:
        raise serializers.ValidationError('Image upload failed — try again.')
    except ValueError:
        raise serializers.ValidationError('Image host returned an invalid response.')

    if not result.get('success'):
        raise serializers.ValidationError('Image upload was rejected by the host.')
    return result['data']['url']
