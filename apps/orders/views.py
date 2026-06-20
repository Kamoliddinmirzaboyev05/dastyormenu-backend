"""Order views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from .models import Order
from .serializers import (
    OrderSerializer, OrderListSerializer,
    OrderStatusSerializer, PublicOrderSerializer
)
from apps.menu.mixins import OrganizationMixin
from apps.users.permissions import IsWaiterOrAbove, IsChefOrAbove


class OrderViewSet(OrganizationMixin, viewsets.ModelViewSet):
    """ViewSet for managing orders."""
    
    queryset = Order.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'table', 'waiter']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    # Allowed order-status transitions (state machine).
    ALLOWED_TRANSITIONS = {
        'pending': {'cooking', 'cancelled'},
        'cooking': {'ready', 'cancelled'},
        'ready': {'completed', 'cancelled'},
        'completed': set(),
        'cancelled': set(),
    }

    throttle_scope = 'public_order'

    def get_permissions(self):
        """Customers create orders publicly (QR-scoped). Everything else is staff-only."""
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['update_status', 'active']:
            return [IsAuthenticated(), IsChefOrAbove()]
        return [IsAuthenticated(), IsWaiterOrAbove()]

    def get_throttles(self):
        # Only throttle the public create endpoint.
        if self.action == 'create':
            return super().get_throttles()
        return []

    def get_serializer_class(self):
        """Return appropriate serializer."""
        # Admin order board needs items + waiter in one call, so use the full
        # serializer for list too (queryset already prefetches items/relations).
        if self.action == 'create':
            return PublicOrderSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        """Public order create: tenant/table/waiter are derived from the QR
        inside the serializer, so bypass the mixin's auth-only org forcing."""
        serializer.save()

    def get_queryset(self):
        """Tenant-scoped (OrganizationMixin) with date-range + table filters."""
        queryset = super().get_queryset().select_related('table', 'waiter').prefetch_related('items')

        table_id = self.request.query_params.get('table_id')
        if table_id:
            queryset = queryset.filter(table_id=table_id)

        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return queryset

    @extend_schema(
        request=OrderStatusSerializer,
        responses={200: OrderSerializer},
        description='Update order status'
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsChefOrAbove])
    def update_status(self, request, pk=None):
        """Update order status with a locked, validated state transition."""
        serializer = OrderStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_status = serializer.validated_data['status']

        # 404 + tenant-scope check via the filtered queryset.
        self.get_object()

        with transaction.atomic():
            # Lock the row so two staff can't transition concurrently.
            order = Order.objects.select_for_update().get(pk=pk)

            if new_status != order.status and new_status not in self.ALLOWED_TRANSITIONS[order.status]:
                return Response(
                    {'error': f'Cannot move order from {order.status} to {new_status}',
                     'code': 'INVALID_TRANSITION'},
                    status=status.HTTP_409_CONFLICT,
                )

            order.status = new_status
            if new_status == 'completed':
                order.completed_at = timezone.now()
            order.save(update_fields=['status', 'completed_at', 'updated_at'])

        return Response(OrderSerializer(order).data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsChefOrAbove])
    def active(self, request):
        """Get active orders for kitchen."""
        queryset = self.get_queryset().filter(
            status__in=['pending', 'cooking', 'ready']
        )
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_tables(self, request):
        """Get orders for waiter's assigned tables."""
        user_profile = request.user.userprofile
        queryset = self.get_queryset().filter(
            waiter=user_profile,
            status__in=['pending', 'cooking', 'ready']
        )
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)


# Public endpoints (no auth required) - DEPRECATED, use OrderViewSet instead
@extend_schema(
    request=PublicOrderSerializer,
    responses={201: PublicOrderSerializer},
    description='Public endpoint for creating orders via QR code (DEPRECATED: use POST /api/orders/ instead)'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def public_create_order(request):
    """Public endpoint for creating orders via QR code."""
    serializer = PublicOrderSerializer(data=request.data)
    
    if serializer.is_valid():
        order = serializer.save()
        return Response(
            PublicOrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    parameters=[
        OpenApiParameter(name='order_id', description='Order ID', required=True, type=str, location=OpenApiParameter.PATH)
    ],
    responses={200: OpenApiResponse(description='Order status')},
    description='Public endpoint for checking order status'
)
@api_view(['GET'])
@permission_classes([AllowAny])
def public_order_status(request, order_id):
    """Public endpoint for checking order status."""
    try:
        order = Order.objects.get(id=order_id)
        return Response({
            'id': str(order.id),
            'status': order.status,
            'table_number': order.table.table_number,
            'total_amount': order.total_amount,
            'created_at': order.created_at
        })
    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found', 'code': 'ORDER_NOT_FOUND'},
            status=status.HTTP_404_NOT_FOUND
        )
