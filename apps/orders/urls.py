"""Order URLs."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, public_create_order, public_order_status

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('public/orders/', public_create_order, name='public-create-order'),
    path('public/orders/<uuid:order_id>/status/', public_order_status, name='public-order-status'),
]
