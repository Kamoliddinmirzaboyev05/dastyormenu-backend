"""Table signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Table


@receiver(post_save, sender=Table)
def generate_qr_on_create(sender, instance: Table, created: bool, **kwargs):
    """Generate QR code when table is created."""
    if created and not instance.qr_code_image:
        instance.generate_qr_code()
        instance.save(update_fields=['qr_code_image'])
