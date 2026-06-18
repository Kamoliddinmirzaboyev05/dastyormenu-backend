"""Payment models."""
import uuid
from django.db import models
from apps.organizations.models import Organization
from apps.orders.models import Order


class Payment(models.Model):
    """Payment for order."""
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('click', 'Click'),
        ('payme', 'Payme'),
        ('card', 'Card'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.IntegerField(help_text='Amount in UZS tiyin')
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='cash'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending'
    )
    transaction_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'payment_status'],
                         name='payment_org_status_idx'),
        ]
    
    def __str__(self) -> str:
        return f"Payment {self.id} - {self.payment_method}"
    
    def mark_paid(self, transaction_id: str = '') -> None:
        """Mark payment as paid."""
        self.payment_status = 'paid'
        if transaction_id:
            self.transaction_id = transaction_id
        self.save(update_fields=['payment_status', 'transaction_id'])
