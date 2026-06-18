"""Payment views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from drf_spectacular.utils import extend_schema
from .models import Payment
from .serializers import PaymentSerializer, PaymentConfirmSerializer
from apps.menu.mixins import OrganizationMixin
from apps.users.permissions import IsManagerOrAbove


class PaymentViewSet(OrganizationMixin, viewsets.ModelViewSet):
    """ViewSet for managing payments (manager-only, tenant-scoped)."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filterset_fields = ['order', 'payment_status', 'payment_method']

    def get_permissions(self):
        # Payments are financial data — managers/super admins only.
        return [IsAuthenticated(), IsManagerOrAbove()]

    def get_queryset(self):
        """Tenant-scoped via OrganizationMixin (Payment has a direct org FK)."""
        return super().get_queryset().select_related('order', 'order__table')

    @extend_schema(
        request=PaymentConfirmSerializer,
        responses={200: PaymentSerializer},
        description='Confirm a pending payment (idempotent, manager-only)'
    )
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Mark a pending payment paid under a row lock; reject double-confirm."""
        serializer = PaymentConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 404 + tenant-scope check.
        self.get_object()

        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(pk=pk)

            if payment.payment_status == 'paid':
                # Idempotent: already confirmed.
                return Response(PaymentSerializer(payment).data)
            if payment.payment_status not in ('pending', 'failed'):
                return Response(
                    {'error': f'Cannot confirm a {payment.payment_status} payment',
                     'code': 'INVALID_PAYMENT_STATE'},
                    status=status.HTTP_409_CONFLICT,
                )

            method = serializer.validated_data.get('payment_method')
            if method:
                payment.payment_method = method
            payment.mark_paid(serializer.validated_data.get('transaction_id', ''))

        return Response(PaymentSerializer(payment).data)
