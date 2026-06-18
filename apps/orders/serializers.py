"""Order serializers."""
from django.db import transaction
from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""
    
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'menu', 'menu_name', 'menu_price',
            'quantity', 'modifications', 'item_status',
            'subtotal', 'created_at'
        ]
        read_only_fields = ['id', 'menu_name', 'menu_price', 'created_at']
    
    def validate_quantity(self, value: int) -> int:
        """Validate quantity is positive."""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    
    items = OrderItemSerializer(many=True)
    table_number = serializers.IntegerField(source='table.table_number', read_only=True)
    waiter_name = serializers.CharField(
        source='waiter.full_name',
        read_only=True,
        allow_null=True
    )
    total_with_tip = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'organization', 'table', 'table_number',
            'waiter', 'waiter_name', 'status', 'total_amount',
            'tip_amount', 'tip_percentage', 'customer_note',
            'total_with_tip', 'items', 'completed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'organization', 'table', 'total_amount', 'completed_at',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'waiter': {'required': False}
        }
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must contain at least one item")
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Create order with items atomically (commit triggers realtime broadcast)."""
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            menu = item_data.get('menu')
            OrderItem.objects.create(
                order=order,
                menu=menu,
                menu_name=menu.name if menu else item_data.get('menu_name', ''),
                menu_price=menu.price if menu else item_data.get('menu_price', 0),
                quantity=item_data.get('quantity', 1),
                modifications=item_data.get('modifications', '')
            )

        order.calculate_total()
        return order



class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order list."""
    
    table_number = serializers.IntegerField(source='table.table_number', read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'table_number', 'status', 'total_amount',
            'items_count', 'created_at'
        ]
    
    def get_items_count(self, obj) -> int:
        """Count items using the prefetched cache (no extra query per row)."""
        return len(obj.items.all())


class OrderStatusSerializer(serializers.Serializer):
    """Serializer for updating order status."""
    
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)


class PublicOrderSerializer(serializers.ModelSerializer):
    """Serializer for public order creation (no auth)."""
    
    items = OrderItemSerializer(many=True)
    qr_code_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'qr_code_id', 'customer_note',
            'tip_amount', 'tip_percentage', 'items',
            'status', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must contain at least one item")
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Create order from QR code atomically.

        Tenant (organization), table and waiter are derived server-side from the
        scanned QR — never trusted from the client.
        """
        from apps.tables.models import Table

        qr_code_id = validated_data.pop('qr_code_id')
        items_data = validated_data.pop('items')

        try:
            table = Table.objects.select_related('organization').get(qr_code_id=qr_code_id)
        except Table.DoesNotExist:
            raise serializers.ValidationError({'qr_code_id': 'Invalid QR code'})

        # Validate every menu item belongs to this tenant and is available
        # BEFORE writing anything.
        for item_data in items_data:
            menu = item_data.get('menu')
            if menu is None:
                raise serializers.ValidationError({'items': 'Each item must reference a menu dish'})
            if menu.organization_id != table.organization_id:
                raise serializers.ValidationError({'items': 'Item does not belong to this restaurant'})
            if not menu.is_available:
                raise serializers.ValidationError({'items': f'{menu.name} is not available'})

        order = Order.objects.create(
            organization=table.organization,
            table=table,
            waiter=table.assigned_waiter,
            **validated_data
        )

        for item_data in items_data:
            menu = item_data['menu']
            OrderItem.objects.create(
                order=order,
                menu=menu,
                menu_name=menu.name,
                menu_price=menu.price,
                quantity=item_data.get('quantity', 1),
                modifications=item_data.get('modifications', '')
            )

        order.calculate_total()
        return order
