"""Notification views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing the current user's notifications."""

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only the authenticated user's own notifications — never cross-user."""
        user = self.request.user
        if not hasattr(user, 'userprofile'):
            return Notification.objects.none()
        return Notification.objects.filter(
            recipient=user.userprofile
        ).select_related('order')
    
    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description='Marked as read')},
        description='Mark notification as read'
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.mark_read()
        return Response({'status': 'marked as read'})
    
    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description='All marked as read')},
        description='Mark all notifications as read'
    )
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all marked as read'})
