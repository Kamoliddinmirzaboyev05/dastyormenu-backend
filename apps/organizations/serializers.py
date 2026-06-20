"""Organization serializers."""
from rest_framework import serializers
from .models import Organization
from apps.utils.images import store_image


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""
    
    is_trial_expired = serializers.ReadOnlyField()
    is_subscription_active = serializers.ReadOnlyField()
    logo_file = serializers.ImageField(write_only=True, required=False, help_text='Upload logo file')
    logo = serializers.URLField(read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'logo', 'logo_file', 'address', 'phone',
            'subscription_plan', 'subscription_status',
            'subscription_expires_at', 'trial_ends_at',
            'monthly_price', 'is_trial_expired',
            'is_subscription_active', 'created_at', 'updated_at'
        ]
        # Billing fields are controlled by super-admin/billing flows only,
        # never editable by a restaurant manager via this serializer.
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'logo',
            'subscription_plan', 'subscription_status',
            'subscription_expires_at', 'trial_ends_at', 'monthly_price',
        ]
    
    def create(self, validated_data):
        """Create organization, storing the uploaded logo (local disk / ImgBB)."""
        logo_file = validated_data.pop('logo_file', None)

        if logo_file:
            validated_data['logo'] = store_image(
                logo_file, self.context.get('request'), 'logos'
            )

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update organization, storing a new logo when provided."""
        logo_file = validated_data.pop('logo_file', None)

        if logo_file:
            validated_data['logo'] = store_image(
                logo_file, self.context.get('request'), 'logos'
            )

        return super().update(instance, validated_data)
    
    def validate_phone(self, value: str) -> str:
        """Validate phone number format."""
        if value and not value.replace('+', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("Invalid phone number format")
        return value


class OrganizationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for organization list."""
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'logo', 'subscription_plan', 'subscription_status']
