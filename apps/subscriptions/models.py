"""Subscription models."""
import uuid
from django.db import models
from apps.organizations.models import Organization


class Subscription(models.Model):
    """Subscription history."""
    
    PLANS = Organization.SUBSCRIPTION_PLANS
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('click', 'Click'),
        ('payme', 'Payme'),
        ('card', 'Card'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='subscription_history'
    )
    plan = models.CharField(max_length=20, choices=PLANS)
    amount = models.IntegerField(help_text='Amount in UZS tiyin')
    paid_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    class Meta:
        db_table = 'subscriptions'
        ordering = ['-paid_at']
    
    def __str__(self) -> str:
        return f"{self.organization.name} - {self.plan}"
