"""Menu models."""
import uuid
from django.db import models
from apps.organizations.models import Organization


class CategoryManager(models.Manager):
    """Custom manager for Category."""
    
    def active(self):
        """Return active categories."""
        return self.filter(is_active=True)


class Category(models.Model):
    """Menu category."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=50, blank=True, help_text='Emoji or icon name')
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CategoryManager()
    
    class Meta:
        db_table = 'categories'
        ordering = ['sort_order', 'name']
        verbose_name_plural = 'Categories'
    
    def __str__(self) -> str:
        return f"{self.icon} {self.name}" if self.icon else self.name


class MenuManager(models.Manager):
    """Custom manager for Menu."""
    
    def available(self):
        """Return available menu items."""
        return self.filter(is_available=True)
    
    def by_category(self, category_id):
        """Return menu items by category."""
        return self.filter(category_id=category_id)


class Menu(models.Model):
    """Menu item (dish)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True, help_text='ImgBB image URL')
    price = models.IntegerField(help_text='Price in UZS tiyin')
    cook_time_minutes = models.IntegerField(default=15)
    ingredients = models.TextField(blank=True)
    is_available = models.BooleanField(default=True, help_text='Stop-list toggle')
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = MenuManager()
    
    class Meta:
        db_table = 'menu_items'
        ordering = ['sort_order', 'name']
        indexes = [
            # Public menu + panel both filter org + availability, ordered by sort.
            models.Index(fields=['organization', 'is_available', 'sort_order'],
                         name='menu_org_avail_sort_idx'),
        ]

    def __str__(self) -> str:
        return self.name
    
    @property
    def price_uzs(self) -> float:
        """Return price in UZS (from tiyin)."""
        return self.price / 100
    
    def toggle_availability(self) -> None:
        """Toggle menu item availability."""
        self.is_available = not self.is_available
        self.save(update_fields=['is_available'])
