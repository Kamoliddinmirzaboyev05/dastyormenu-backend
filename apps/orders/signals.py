"""Order signals.

Real-time broadcasts and payment creation run on transaction commit so the
kitchen never receives a half-built order (items + total are guaranteed
present), and a Redis/channel outage can't roll back the DB write.
"""
import logging
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Order

logger = logging.getLogger(__name__)


def _broadcast(group: str, payload: dict) -> None:
    """Send to a channel group, swallowing channel-layer errors."""
    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        async_to_sync(channel_layer.group_send)(group, payload)
    except Exception:  # pragma: no cover - best-effort realtime
        logger.exception('Channel broadcast failed for group %s', group)


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance: Order, created: bool, **kwargs):
    """Notify kitchen/waiter and create payment, after the tx commits."""
    order_id = str(instance.id)
    org_id = instance.organization_id
    kitchen_group = f'org_{org_id}_kitchen'

    if created:
        def on_commit_new():
            # Re-read so total/items reflect the fully-built order.
            order = Order.objects.select_related('table', 'waiter').filter(pk=instance.pk).first()
            if not order:
                return
            _broadcast(kitchen_group, {
                'type': 'order_update',
                'action': 'new_order',
                'order_id': order_id,
                'status': order.status,
                'table_number': order.table.table_number,
                'total_amount': order.total_amount,
            })
            from apps.notifications.models import Notification
            Notification.objects.create(
                organization=order.organization,
                recipient=order.waiter,
                type='new_order',
                message=f'New order from Table {order.table.table_number}',
                order=order,
            )
        transaction.on_commit(on_commit_new)
        return

    status = instance.status

    if status == 'cooking':
        transaction.on_commit(lambda: _broadcast(kitchen_group, {
            'type': 'order_update',
            'action': 'status_changed',
            'order_id': order_id,
            'status': status,
        }))

    elif status == 'ready' and instance.waiter_id:
        waiter_id = str(instance.waiter_id)
        table_number = instance.table.table_number

        def on_commit_ready():
            _broadcast(f'user_{waiter_id}', {
                'type': 'notification',
                'message': f'Order for Table {table_number} is ready',
                'order_id': order_id,
            })
            from apps.notifications.models import Notification
            Notification.objects.create(
                organization_id=org_id,
                recipient_id=instance.waiter_id,
                type='order_ready',
                message=f'Order for Table {table_number} is ready',
                order_id=instance.pk,
            )
        transaction.on_commit(on_commit_ready)

    elif status == 'completed':
        def on_commit_completed():
            from apps.payments.models import Payment
            Payment.objects.get_or_create(
                order_id=instance.pk,
                defaults={
                    'organization_id': org_id,
                    'amount': instance.total_with_tip,
                    'payment_status': 'pending',
                },
            )
        transaction.on_commit(on_commit_completed)
