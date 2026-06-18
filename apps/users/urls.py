"""User URLs."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, login_view, pin_login_view, logout_view
from .auth import CookieTokenRefreshView

router = DefaultRouter()
router.register(r'users', UserProfileViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', login_view, name='login'),
    path('auth/pin-login/', pin_login_view, name='pin-login'),
    path('auth/logout/', logout_view, name='logout'),
    # Refresh reads the httpOnly cookie, not the request body.
    path('auth/refresh/', CookieTokenRefreshView.as_view(), name='token-refresh'),
]
