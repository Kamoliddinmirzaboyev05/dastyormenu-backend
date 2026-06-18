"""Subscription views."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Subscription
from .serializers import SubscriptionSerializer
from apps.users.permissions import IsManagerOrAbove


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing the current org's subscriptions (manager-only)."""

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]

    def get_queryset(self):
        """Tenant-scoped to the authenticated manager's organization."""
        user = self.request.user
        if not hasattr(user, 'userprofile'):
            return Subscription.objects.none()
        profile = user.userprofile
        if profile.role == 'super_admin':
            return Subscription.objects.all()
        if profile.organization_id:
            return Subscription.objects.filter(organization_id=profile.organization_id)
        return Subscription.objects.none()

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current subscription info."""
        user = request.user
        if hasattr(user, 'userprofile') and user.userprofile.organization:
            org = user.userprofile.organization
            return Response({
                'plan': org.subscription_plan,
                'status': org.subscription_status,
                'expires_at': org.subscription_expires_at,
                'trial_ends_at': org.trial_ends_at,
                'is_active': org.is_subscription_active
            })
        return Response({'error': 'User profile not found'}, status=404)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get subscription payment history."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
