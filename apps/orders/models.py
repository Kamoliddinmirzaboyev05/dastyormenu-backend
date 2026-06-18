"""Order models."""
import uuid
from django.db import models
from django.utils import timezone
from apps.organizations.models import Organization
from apps.tables.models import Table
from apps.users.models import UserProfile
from apps.menu.models import Menu


class OrderManager(models.Manager):
    """Custom manager for Order."""
    
    def active(self):
        """Return active orders (not completed/cancelled)."""
        return self.filter(status__in=['pending', 'cooking', 'ready'])
    
    def pending(self):
        """Return pending orders."""
        return self.filter(status='pending')
    
    def cooking(self):
        """Return cooking orders."""
        return self.filter(status='cooking')
    
    def ready(self):
        """Return ready orders."""
        return self.filter(status='ready')


class Order(models.Model):
    """Customer order."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('cooking', 'Cooking'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    waiter = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    total_amount = models.IntegerField(default=0, help_text='Total in UZS tiyin')
    tip_amount = models.IntegerField(default=0, help_text='Tip in UZS tiyin')
    tip_percentage = models.IntegerField(default=0)
    customer_note = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            # Kitchen board / active-order queries are always org + status.
            models.Index(fields=['organization', 'status'], name='order_org_status_idx'),
            # Dashboard date-range listing.
            models.Index(fields=['organization', '-created_at'], name='order_org_created_idx'),
        ]

    def __str__(self) -> str:
        return f"Order {self.id} - Table {self.table.table_number}"
    
    def calculate_total(self) -> None:
        """Calculate total amount from order items."""
        total = sum(item.menu_price * item.quantity for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])
    
    def mark_completed(self) -> None:
        """Mark order as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
    
    @property
    def total_with_tip(self) -> int:
        """Get total amount including tip."""
        return self.total_amount + self.tip_amount


class OrderItem(models.Model):
    """Order item (dish in order)."""
    
    STATUS_CHOICES = Order.STATUS_CHOICES
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    menu_name = models.CharField(max_length=255, help_text='Snapshot of menu name')
    menu_price = models.IntegerField(help_text='Snapshot of price in UZS tiyin')
    quantity = models.IntegerField(default=1)
    modifications = models.TextField(blank=True, help_text='Special requests')
    item_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'order_items'
        ordering = ['created_at']
    
    def __str__(self) -> str:
        return f"{self.quantity}x {self.menu_name}"
    
    @property
    def subtotal(self) -> int:
        """Calculate subtotal for this item."""
        return self.menu_price * self.quantity
