"""User models."""
import uuid
import bcrypt
from django.db import models
from django.contrib.auth.models import User
from apps.organizations.models import Organization


class UserProfileManager(models.Manager):
    """Custom manager for UserProfile."""
    
    def chefs(self):
        """Return chef users."""
        return self.filter(role='chef', is_active=True)
    
    def waiters(self):
        """Return waiter users."""
        return self.filter(role='waiter', is_active=True)
    
    def managers(self):
        """Return manager users."""
        return self.filter(role__in=['manager', 'super_admin'], is_active=True)


class UserProfile(models.Model):
    """Extended user profile with organization and role."""
    
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('manager', 'Manager'),
        ('chef', 'Chef'),
        ('waiter', 'Waiter'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True,
        help_text='Organization (not required for super_admin)'
    )
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    pin_code = models.CharField(max_length=255, blank=True, help_text='Bcrypt hashed PIN')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserProfileManager()
    
    class Meta:
        db_table = 'user_profiles'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.full_name} ({self.role})"
    
    def set_pin(self, pin: str) -> None:
        """Hash and set PIN code."""
        if len(pin) != 4 or not pin.isdigit():
            raise ValueError("PIN must be 4 digits")
        hashed = bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt())
        self.pin_code = hashed.decode('utf-8')
    
    def check_pin(self, pin: str) -> bool:
        """Verify PIN code."""
        if not self.pin_code:
            return False
        return bcrypt.checkpw(pin.encode('utf-8'), self.pin_code.encode('utf-8'))
    
    @property
    def is_super_admin(self) -> bool:
        """Check if user is super admin."""
        return self.role == 'super_admin'
    
    @property
    def is_manager(self) -> bool:
        """Check if user is manager or above."""
        return self.role in ['super_admin', 'manager']
    
    @property
    def is_chef(self) -> bool:
        """Check if user is chef or above."""
        return self.role in ['super_admin', 'manager', 'chef']
    
    @property
    def is_waiter(self) -> bool:
        """Check if user is waiter or above."""
        return self.role in ['super_admin', 'manager', 'chef', 'waiter']
