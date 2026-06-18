"""Custom exception handler for standardized error responses."""
from django.conf import settings
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Return a standardized error envelope: {"error": ..., "code": "ERROR_CODE"}.

    DRF-handled errors (validation, auth, permission, 404) keep their detail.
    Unhandled exceptions (500s) return a generic message and never leak
    internals/tracebacks to clients in production.
    """
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled server error. Let Django's 500 handling/logging happen in
        # DEBUG; in production return a safe generic payload.
        if settings.DEBUG:
            return None
        from rest_framework.response import Response
        from rest_framework import status
        return Response(
            {'error': 'Internal server error', 'code': 'SERVER_ERROR'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    error_data = {'code': exc.__class__.__name__.upper()}
    detail = getattr(exc, 'detail', None)
    if isinstance(detail, dict):
        error_data['error'] = detail
    elif detail is not None:
        error_data['error'] = str(detail)
    else:
        error_data['error'] = str(exc)

    response.data = error_data
    return response
