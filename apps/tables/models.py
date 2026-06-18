"""Table models."""
import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.core.files import File
from django.conf import settings
from apps.organizations.models import Organization
from apps.users.models import UserProfile


class TableManager(models.Manager):
    """Custom manager for Table."""
    
    def active(self):
        """Return active tables."""
        return self.filter(is_active=True)


class Table(models.Model):
    """Restaurant table."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='tables'
    )
    table_number = models.IntegerField()
    qr_code_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    qr_code_image = models.ImageField(upload_to='tables/qr_codes/', null=True, blank=True)
    assigned_waiter = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tables'
    )
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TableManager()
    
    class Meta:
        db_table = 'tables'
        ordering = ['table_number']
        unique_together = ['organization', 'table_number']
    
    def __str__(self) -> str:
        return f"Table {self.table_number}"
    
    def generate_qr_code(self) -> None:
        """Generate QR code for table."""
        qr_url = f"{settings.BASE_URL}/menu?qr={self.qr_code_id}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        filename = f'table_{self.table_number}_{self.qr_code_id}.png'
        self.qr_code_image.save(filename, File(buffer), save=False)
    
    def regenerate_qr_code(self) -> None:
        """Regenerate QR code with new ID."""
        self.qr_code_id = uuid.uuid4()
        self.generate_qr_code()
        self.save()
