"""User serializers."""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""
    
    user = UserSerializer(read_only=True)
    email = serializers.EmailField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    pin_code = serializers.CharField(write_only=True, required=False, max_length=4)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'organization', 'full_name', 'role',
            'is_active', 'email', 'password', 'pin_code',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'organization': {'required': False}
        }
    
    def create(self, validated_data):
        """Create user with profile."""
        email = validated_data.pop('email', None)
        password = validated_data.pop('password', None)
        pin_code = validated_data.pop('pin_code', None)
        role = validated_data.get('role', 'waiter')
        
        # Create Django user
        user = User.objects.create_user(
            username=email or f"user_{validated_data['full_name']}",
            email=email,
            password=password
        )
        
        # Super admin doesn't need organization
        if role == 'super_admin' and 'organization' not in validated_data:
            validated_data['organization'] = None
        
        # Create profile
        profile = UserProfile.objects.create(user=user, **validated_data)
        
        # Set PIN if provided
        if pin_code:
            profile.set_pin(pin_code)
            profile.save()
        
        return profile
    
    def validate_pin_code(self, value):
        """Validate PIN code format."""
        if value and (len(value) != 4 or not value.isdigit()):
            raise serializers.ValidationError("PIN must be exactly 4 digits")
        return value


class SetPinSerializer(serializers.Serializer):
    """Serializer for setting user PIN."""
    
    pin_code = serializers.CharField(max_length=4, min_length=4)
    
    def validate_pin_code(self, value):
        """Validate PIN is 4 digits."""
        if not value.isdigit():
            raise serializers.ValidationError("PIN must contain only digits")
        return value


class LoginSerializer(serializers.Serializer):
    """Serializer for login/password authentication."""
    
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)


class PinLoginSerializer(serializers.Serializer):
    """Serializer for PIN login."""
    
    organization_id = serializers.UUIDField()
    pin_code = serializers.CharField(max_length=4, min_length=4)
    
    def validate_pin_code(self, value):
        """Validate PIN format."""
        if not value.isdigit():
            raise serializers.ValidationError("PIN must be 4 digits")
        return value
