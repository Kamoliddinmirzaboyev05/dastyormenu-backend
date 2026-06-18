"""Order WebSocket consumers."""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from urllib.parse import parse_qs


class OrderConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time order updates."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        # Get token from query params
        query_string = self.scope['query_string'].decode()
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]
        
        if not token:
            await self.close()
            return
        
        # Authenticate user
        user = await self.get_user_from_token(token)
        if not user or not hasattr(user, 'userprofile'):
            await self.close()
            return
        
        self.user = user
        self.organization_id = str(user.userprofile.organization_id)
        
        # Join kitchen group
        self.kitchen_group = f'org_{self.organization_id}_kitchen'
        await self.channel_layer.group_add(
            self.kitchen_group,
            self.channel_name
        )
        
        await self.accept()
        
        # Send active orders
        orders = await self.get_active_orders()
        await self.send(text_data=json.dumps({
            'type': 'active_orders',
            'orders': orders
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'kitchen_group'):
            await self.channel_layer.group_discard(
                self.kitchen_group,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'ping':
            await self.send(text_data=json.dumps({'type': 'pong'}))
    
    async def order_update(self, event):
        """Handle order update events."""
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
    def get_active_orders(self):
        """Get active orders for organization."""
        from .models import Order
        from .serializers import OrderSerializer
        
        orders = Order.objects.filter(
            organization_id=self.organization_id,
            status__in=['pending', 'cooking', 'ready']
        ).select_related('table', 'waiter').prefetch_related('items')
        
        return [OrderSerializer(order).data for order in orders]
