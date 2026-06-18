"""WebSocket URL routing."""
from django.urls import path
from apps.orders.consumers import OrderConsumer
from apps.notifications.consumers import NotificationConsumer

websocket_urlpatterns = [
    path('ws/orders/', OrderConsumer.as_asgi()),
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]
