"""Notification WebSocket consumers."""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from urllib.parse import parse_qs


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        query_string = self.scope['query_string'].decode()
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]
        
        if not token:
            await self.close()
            return
        
        user = await self.get_user_from_token(token)
        if not user or not hasattr(user, 'userprofile'):
            await self.close()
            return
        
        self.user = user
        self.user_id = str(user.userprofile.id)
        
        # Join user's personal notification group
        self.user_group = f'user_{self.user_id}'
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        
        await self.accept()
        
        # Send unread notifications
        notifications = await self.get_unread_notifications()
        await self.send(text_data=json.dumps({
            'type': 'unread_notifications',
            'notifications': notifications
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'ping':
            await self.send(text_data=json.dumps({'type': 'pong'}))
    
    async def notification(self, event):
        """Handle notification events."""
        await self.send(text_data=json.dumps(event))
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        """Get user from JWT token."""
        from rest_framework_simplejwt.tokens import AccessToken
        from django.contrib.auth.models import User
        
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except Exception:
            return None
    
    @database_sync_to_async
    def get_unread_notifications(self):
        """Get unread notifications for user."""
        from .models import Notification
        from .serializers import NotificationSerializer
        
        notifications = Notification.objects.filter(
            recipient=self.user.userprofile,
            is_read=False
        )[:20]
        
        return [NotificationSerializer(n).data for n in notifications]
