"""User signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_superuser_profile(sender, instance, created, **kwargs):
    """Auto-create a profile ONLY for Django superusers (createsuperuser/admin).

    Regular staff are created through the API (UserProfileSerializer), which
    assigns the correct organization explicitly. We must NOT auto-assign normal
    users to ``Organization.objects.first()`` — that silently leaks new users
    into an arbitrary tenant and collides with the explicit profile creation.
    """
    if not created or not instance.is_superuser:
        return
    if hasattr(instance, 'userprofile'):
        return
    UserProfile.objects.create(
        user=instance,
        organization=None,
        full_name=instance.get_full_name() or instance.username,
        role='super_admin',
        is_active=True,
    )
