"""Notification models."""
import uuid
from django.db import models
from apps.organizations.models import Organization
from apps.users.models import UserProfile
from apps.orders.models import Order


class NotificationManager(models.Manager):
    """Custom manager for Notification."""
    
    def unread(self):
        """Return unread notifications."""
        return self.filter(is_read=False)


class Notification(models.Model):
    """User notification."""
    
    NOTIFICATION_TYPES = [
        ('order_ready', 'Order Ready'),
        ('waiter_call', 'Waiter Call'),
        ('bill_request', 'Bill Request'),
        ('new_order', 'New Order'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    recipient = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = NotificationManager()
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            # "My unread notifications, newest first" is the hot query.
            models.Index(fields=['recipient', 'is_read', '-created_at'],
                         name='notif_recipient_read_idx'),
        ]
    
    def __str__(self) -> str:
        return f"{self.type} - {self.message[:50]}"
    
    def mark_read(self) -> None:
        """Mark notification as read."""
        self.is_read = True
        self.save(update_fields=['is_read'])
