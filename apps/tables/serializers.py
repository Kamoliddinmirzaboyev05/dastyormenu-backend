"""Table serializers."""
from rest_framework import serializers
from .models import Table


class TableSerializer(serializers.ModelSerializer):
    """Serializer for Table model."""
    
    waiter_name = serializers.CharField(
        source='assigned_waiter.full_name',
        read_only=True,
        allow_null=True
    )
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Table
        fields = [
            'id', 'organization', 'table_number', 'qr_code_id',
            'qr_code_image', 'qr_code_url', 'assigned_waiter',
            'waiter_name', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'qr_code_id', 'qr_code_image', 'created_at', 'updated_at']
        extra_kwargs = {
            'organization': {'required': False}
        }
    
    def get_qr_code_url(self, obj) -> str:
        """Get full URL for QR code image."""
        if obj.qr_code_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code_image.url)
            return obj.qr_code_image.url
        return None
    
    def validate_table_number(self, value: int) -> int:
        """Validate table number is positive."""
        if value < 1:
            raise serializers.ValidationError("Table number must be positive")
        return value


class TableListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for table list."""
    
    waiter_name = serializers.CharField(
        source='assigned_waiter.full_name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = Table
        fields = ['id', 'table_number', 'waiter_name', 'is_active']
