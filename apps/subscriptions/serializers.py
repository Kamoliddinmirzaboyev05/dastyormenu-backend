"""Subscription serializers."""
from rest_framework import serializers
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model."""
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'organization', 'plan', 'amount',
            'paid_at', 'expires_at', 'payment_method'
        ]
        read_only_fields = ['id', 'paid_at']
