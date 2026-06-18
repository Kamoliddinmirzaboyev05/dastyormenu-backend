"""User views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import UserProfile
from .serializers import (
    UserProfileSerializer, SetPinSerializer,
    LoginSerializer, PinLoginSerializer
)
from .permissions import IsManagerOrAbove
from .auth import issue_tokens, delete_refresh_cookie


class LoginThrottle(ScopedRateThrottle):
    scope = 'login'


class PinLoginThrottle(ScopedRateThrottle):
    scope = 'pin_login'


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user profiles."""
    
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]
    
    def get_queryset(self):
        """Filter users by organization."""
        user = self.request.user
        if hasattr(user, 'userprofile'):
            if user.userprofile.role == 'super_admin':
                return UserProfile.objects.all()
            return UserProfile.objects.filter(
                organization=user.userprofile.organization
            )
        return UserProfile.objects.none()
    
    def perform_create(self, serializer):
        """Force the new user into the manager's own organization.

        Only a super_admin may target a different organization explicitly.
        """
        actor = self.request.user.userprofile
        if actor.role == 'super_admin':
            serializer.save()
        else:
            # Never trust a client-supplied organization for non-super users.
            serializer.save(organization=actor.organization)
    
    @extend_schema(
        request=SetPinSerializer,
        responses={200: OpenApiResponse(description='PIN set successfully')}
    )
    @action(detail=True, methods=['post'])
    def set_pin(self, request, pk=None):
        """Set PIN code for user."""
        user_profile = self.get_object()
        serializer = SetPinSerializer(data=request.data)
        
        if serializer.is_valid():
            user_profile.set_pin(serializer.validated_data['pin_code'])
            user_profile.save()
            return Response({'status': 'PIN set successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
    request=LoginSerializer,
    responses={200: UserProfileSerializer},
    description='Login with username/email and password'
)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle])
def login_view(request):
    """Login with username/email + password. Returns access token in body and
    sets the refresh token as an httpOnly cookie."""
    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    login_input = serializer.validated_data['login']
    password = serializer.validated_data['password']

    # Try username, then email.
    user = authenticate(username=login_input, password=password)
    if not user:
        from django.contrib.auth.models import User
        match = User.objects.filter(email__iexact=login_input).first()
        if match:
            user = authenticate(username=match.username, password=password)

    if not user:
        return Response(
            {'error': 'Invalid credentials', 'code': 'INVALID_CREDENTIALS'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not hasattr(user, 'userprofile'):
        return Response(
            {'error': 'User profile not found', 'code': 'PROFILE_NOT_FOUND'},
            status=status.HTTP_404_NOT_FOUND
        )
    if not user.userprofile.is_active:
        return Response(
            {'error': 'Account disabled', 'code': 'ACCOUNT_DISABLED'},
            status=status.HTTP_403_FORBIDDEN
        )

    return issue_tokens(
        {'user': UserProfileSerializer(user.userprofile).data}, user
    )


@extend_schema(
    request=PinLoginSerializer,
    responses={200: UserProfileSerializer},
    description='PIN login endpoint for chefs and waiters'
)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PinLoginThrottle])
def pin_login_view(request):
    """PIN login for chefs/waiters. Throttled to blunt brute-force; sets the
    refresh cookie like the password login."""
    serializer = PinLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    organization_id = serializer.validated_data['organization_id']
    pin_code = serializer.validated_data['pin_code']

    profiles = UserProfile.objects.filter(
        organization_id=organization_id,
        is_active=True,
    ).exclude(pin_code='').select_related('user')

    for profile in profiles:
        if profile.check_pin(pin_code):
            return issue_tokens(
                {'user': UserProfileSerializer(profile).data}, profile.user
            )

    return Response(
        {'error': 'Invalid PIN or organization', 'code': 'INVALID_PIN'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@extend_schema(
    request=None,
    responses={200: OpenApiResponse(description='Logged out successfully')},
    description='Logout endpoint'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Blacklist the refresh token (from the cookie) and clear the cookie."""
    raw_refresh = request.COOKIES.get(settings.AUTH_COOKIE_NAME)
    if raw_refresh:
        try:
            RefreshToken(raw_refresh).blacklist()
        except (TokenError, AttributeError):
            pass

    response = Response({'status': 'logged out successfully'})
    delete_refresh_cookie(response)
    return response
