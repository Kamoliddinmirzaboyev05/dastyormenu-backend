"""Organization signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Organization


@receiver(post_save, sender=Organization)
def set_trial_period(sender, instance: Organization, created: bool, **kwargs):
    """Set trial period when organization is created."""
    if created and instance.subscription_plan == 'trial':
        if not instance.trial_ends_at:
            instance.trial_ends_at = timezone.now() + timedelta(days=14)
            instance.subscription_expires_at = instance.trial_ends_at
            instance.save(update_fields=['trial_ends_at', 'subscription_expires_at'])
