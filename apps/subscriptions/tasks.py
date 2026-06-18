"""Subscription Celery tasks."""
from celery import shared_task
from django.utils import timezone
from apps.organizations.models import Organization
from apps.notifications.models import Notification


@shared_task
def check_expired_subscriptions():
    """Check and deactivate expired subscriptions."""
    now = timezone.now()
    
    # Find expired subscriptions
    expired_orgs = Organization.objects.filter(
        subscription_status=True,
        subscription_expires_at__lt=now
    )
    
    for org in expired_orgs:
        # Deactivate subscription
        org.subscription_status = False
        org.save(update_fields=['subscription_status'])
        
        # Notify managers
        managers = org.users.filter(role__in=['manager', 'super_admin'])
        for manager in managers:
            Notification.objects.create(
                organization=org,
                recipient=manager,
                type='bill_request',
                message=f'Subscription expired for {org.name}. Please renew.'
            )
    
    return f'Deactivated {expired_orgs.count()} expired subscriptions'
