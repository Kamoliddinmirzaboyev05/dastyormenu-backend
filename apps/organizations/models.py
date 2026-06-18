"""Organization models."""
import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta


class OrganizationManager(models.Manager):
    """Custom manager for Organization model."""
    
    def active(self):
        """Return organizations with active subscriptions."""
        return self.filter(subscription_status=True)
    
    def trial(self):
        """Return organizations on trial."""
        return self.filter(subscription_plan='trial')


class Organization(models.Model):
    """Restaurant/Cafe organization (tenant)."""
    
    SUBSCRIPTION_PLANS = [
        ('trial', 'Trial'),
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    logo = models.URLField(max_length=500, null=True, blank=True, help_text='ImgBB logo URL')
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    subscription_plan = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_PLANS,
        default='trial'
    )
    subscription_status = models.BooleanField(default=True)
    subscription_expires_at = models.DateTimeField(null=True, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    monthly_price = models.IntegerField(
        default=0,
        help_text='Monthly price in UZS tiyin'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrganizationManager()
    
    class Meta:
        db_table = 'organizations'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        """Set trial period on creation."""
        if not self.pk and self.subscription_plan == 'trial':
            self.trial_ends_at = timezone.now() + timedelta(days=14)
            self.subscription_expires_at = self.trial_ends_at
        super().save(*args, **kwargs)
    
    @property
    def is_trial_expired(self) -> bool:
        """Check if trial period has expired."""
        if self.trial_ends_at:
            return timezone.now() > self.trial_ends_at
        return False
    
    @property
    def is_subscription_active(self) -> bool:
        """Check if subscription is active."""
        if not self.subscription_status:
            return False
        if self.subscription_expires_at:
            return timezone.now() < self.subscription_expires_at
        return True
