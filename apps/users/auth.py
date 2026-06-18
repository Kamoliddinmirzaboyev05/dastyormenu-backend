"""httpOnly refresh-cookie helpers and a cookie-based token refresh view.

The access token lives only in the SPA's memory; the refresh token is delivered
as a hardened httpOnly cookie so XSS cannot read it. The browser sends the
cookie automatically to /api/auth/refresh/ and /api/auth/logout/.
"""
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema


def set_refresh_cookie(response, refresh_token: str) -> None:
    """Attach the refresh token as a hardened httpOnly cookie."""
    max_age = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=str(refresh_token),
        max_age=max_age,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        domain=settings.AUTH_COOKIE_DOMAIN,
        path=settings.AUTH_COOKIE_PATH,
    )


def delete_refresh_cookie(response) -> None:
    response.delete_cookie(
        key=settings.AUTH_COOKIE_NAME,
        path=settings.AUTH_COOKIE_PATH,
        domain=settings.AUTH_COOKIE_DOMAIN,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


def issue_tokens(response_data: dict, user) -> Response:
    """Build a login response: access token in body, refresh token in cookie."""
    refresh = RefreshToken.for_user(user)
    response_data['access'] = str(refresh.access_token)
    response = Response(response_data)
    set_refresh_cookie(response, str(refresh))
    return response


class CookieTokenRefreshThrottle(ScopedRateThrottle):
    scope = 'login'


@extend_schema(
    request=None,
    responses={200: {'type': 'object', 'properties': {'access': {'type': 'string'}}}},
    description='Refresh the access token using the httpOnly refresh cookie.',
)
class CookieTokenRefreshView(APIView):
    """Refresh the access token using the httpOnly refresh cookie.

    Reads the refresh token from the cookie (never the body), rotates it, sets
    the new refresh cookie, and returns the new access token in the body.
    """
    permission_classes = [AllowAny]
    throttle_classes = [CookieTokenRefreshThrottle]

    def post(self, request, *args, **kwargs):
        raw_refresh = request.COOKIES.get(settings.AUTH_COOKIE_NAME)
        if not raw_refresh:
            return Response(
                {'error': 'No refresh token', 'code': 'NO_REFRESH_TOKEN'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(raw_refresh)
        except TokenError:
            resp = Response(
                {'error': 'Invalid or expired refresh token', 'code': 'INVALID_REFRESH'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            delete_refresh_cookie(resp)
            return resp

        # No rotation: just hand back a new access token.
        if not settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS'):
            return Response({'access': str(refresh.access_token)})

        # Rotation: blacklist the presented token, mint a fresh refresh + access.
        user_id = refresh.get(settings.SIMPLE_JWT.get('USER_ID_CLAIM', 'user_id'))
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            resp = Response(
                {'error': 'Invalid token subject', 'code': 'INVALID_REFRESH'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            delete_refresh_cookie(resp)
            return resp

        if settings.SIMPLE_JWT.get('BLACKLIST_AFTER_ROTATION'):
            try:
                refresh.blacklist()
            except AttributeError:
                pass

        new_refresh = RefreshToken.for_user(user)
        response = Response({'access': str(new_refresh.access_token)})
        set_refresh_cookie(response, str(new_refresh))
        return response
