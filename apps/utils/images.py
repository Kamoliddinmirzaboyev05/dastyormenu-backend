"""Shared image-upload helper (ImgBB) with validation.

Single source of truth used by menu + organization serializers so upload
limits, timeouts and error handling stay consistent.
"""
import base64
import requests
from django.conf import settings
from rest_framework import serializers

MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
UPLOAD_TIMEOUT = 15  # seconds


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
