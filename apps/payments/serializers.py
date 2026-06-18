"""Payment serializers."""
from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    
    order_id = serializers.UUIDField(source='order.id', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'organization', 'order', 'order_id',
            'amount', 'payment_method', 'payment_status',
            'transaction_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'organization': {'required': False}
        }


class PaymentConfirmSerializer(serializers.Serializer):
    """Serializer for confirming payment."""

    transaction_id = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(
        choices=Payment.PAYMENT_METHODS, required=False
    )
