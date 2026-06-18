"""Notification serializers."""
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    
    order_id = serializers.UUIDField(source='order.id', read_only=True, allow_null=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'organization', 'recipient', 'type',
            'message', 'order', 'order_id', 'is_read',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
