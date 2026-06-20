"""Menu serializers."""
from rest_framework import serializers
from .models import Category, Menu
from apps.utils.images import store_image


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'organization', 'name', 'icon',
            'sort_order', 'is_active', 'items_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'organization': {'required': False}
        }
    
    def get_items_count(self, obj) -> int:
        """Get count of items in category."""
        return obj.items.filter(is_available=True).count()


class MenuSerializer(serializers.ModelSerializer):
    """Serializer for Menu model."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    price_uzs = serializers.ReadOnlyField()
    image = serializers.ImageField(write_only=True, required=False, help_text='Upload image file')
    image_url = serializers.URLField(read_only=True)
    
    class Meta:
        model = Menu
        fields = [
            'id', 'organization', 'category', 'category_name',
            'name', 'description', 'image', 'image_url', 'price', 'price_uzs',
            'cook_time_minutes', 'ingredients', 'is_available',
            'sort_order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'image_url']
        extra_kwargs = {
            'organization': {'required': False}
        }
    
    def create(self, validated_data):
        """Create menu item, storing the uploaded image (local disk / ImgBB)."""
        image_file = validated_data.pop('image', None)

        if image_file:
            validated_data['image_url'] = store_image(
                image_file, self.context.get('request'), 'menu'
            )

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update menu item, storing a new image when provided."""
        image_file = validated_data.pop('image', None)

        if image_file:
            validated_data['image_url'] = store_image(
                image_file, self.context.get('request'), 'menu'
            )

        return super().update(instance, validated_data)
    
    def validate_price(self, value: int) -> int:
        """Validate price is positive."""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value
    
    def validate_cook_time_minutes(self, value: int) -> int:
        """Validate cook time is positive."""
        if value < 0:
            raise serializers.ValidationError("Cook time cannot be negative")
        return value


class MenuListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for menu list."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.UUIDField(source='category.id', read_only=True)
    price_uzs = serializers.ReadOnlyField()
    
    class Meta:
        model = Menu
        fields = [
            'id', 'name', 'description', 'image_url', 'price', 'price_uzs',
            'category_id', 'category_name', 'ingredients',
            'is_available', 'cook_time_minutes', 'sort_order'
        ]
