"""Table views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from .models import Table
from .serializers import TableSerializer, TableListSerializer
from apps.menu.mixins import OrganizationMixin
from apps.users.permissions import IsManagerOrAbove


class TableViewSet(OrganizationMixin, viewsets.ModelViewSet):
    """ViewSet for managing tables."""
    
    queryset = Table.objects.all()
    
    def get_permissions(self):
        """qr_lookup is public (QR-scoped). Listing/managing tables is staff-only."""
        if self.action == 'qr_lookup':
            return [AllowAny()]
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]

    def get_queryset(self):
        """Tenant-scoped via OrganizationMixin."""
        return super().get_queryset().select_related('organization', 'assigned_waiter')

    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'list':
            return TableListSerializer
        return TableSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='qr', description='QR code ID', required=True, type=str)
        ],
        responses={200: TableSerializer},
        description='Public endpoint for looking up table by QR code'
    )
    @action(detail=False, methods=['get'], url_path='qr-lookup')
    def qr_lookup(self, request):
        """Public endpoint for looking up table by QR code."""
        qr_code_id = request.query_params.get('qr')
        
        if not qr_code_id:
            return Response(
                {'error': 'QR code ID required', 'code': 'QR_REQUIRED'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            table = Table.objects.select_related('organization').get(qr_code_id=qr_code_id)
        except Table.DoesNotExist:
            return Response(
                {'error': 'Invalid QR code', 'code': 'INVALID_QR'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(table)
        return Response({
            'table': serializer.data,
            'organization': {
                'id': str(table.organization.id),
                'name': table.organization.name,
                'logo': table.organization.logo or None,
            }
        })
    
    @action(detail=True, methods=['get'])
    def qr_code(self, request, pk=None):
        """Download QR code image."""
        table = self.get_object()
        
        if not table.qr_code_image:
            return Response(
                {'error': 'QR code not generated', 'code': 'QR_NOT_FOUND'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = HttpResponse(table.qr_code_image.read(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="table_{table.table_number}_qr.png"'
        return response
    
    @extend_schema(
        request=None,
        responses={200: TableSerializer},
        description='Regenerate QR code for table'
    )
    @action(detail=True, methods=['post'])
    def regenerate_qr(self, request, pk=None):
        """Regenerate QR code for table."""
        table = self.get_object()
        table.regenerate_qr_code()
        serializer = self.get_serializer(table)
        return Response(serializer.data)
