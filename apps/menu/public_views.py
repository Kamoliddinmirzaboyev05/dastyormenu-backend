"""Public menu views (no authentication required)."""
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter
from apps.tables.models import Table
from .models import Menu, Category
from .serializers import MenuListSerializer, CategorySerializer


class PublicMenuThrottle(ScopedRateThrottle):
    scope = 'public_menu'


@extend_schema(
    parameters=[
        OpenApiParameter(name='qr', description='QR code ID', required=True, type=str)
    ],
    responses={200: MenuListSerializer(many=True)},
    description='Public endpoint for viewing a single restaurant menu via QR code'
)
@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([PublicMenuThrottle])
def public_menu(request):
    """Return one restaurant's menu + categories, resolved from the table QR.

    This is the ONLY tenant-scoped public menu path — items are always filtered
    to the QR's organization, so customers never see another restaurant's menu.
    """
    qr_code_id = request.query_params.get('qr')

    if not qr_code_id:
        return Response(
            {'error': 'QR code ID required', 'code': 'QR_REQUIRED'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        table = Table.objects.select_related('organization').get(qr_code_id=qr_code_id)
    except (Table.DoesNotExist, ValueError, ValidationError):
        return Response(
            {'error': 'Invalid QR code', 'code': 'INVALID_QR'},
            status=status.HTTP_404_NOT_FOUND
        )

    org = table.organization

    menu_items = Menu.objects.filter(
        organization=org,
        is_available=True,
    ).select_related('category').order_by('sort_order', 'name')

    categories = Category.objects.filter(
        organization=org,
        is_active=True,
    ).order_by('sort_order', 'name')

    return Response({
        'organization': {
            'id': str(org.id),
            'name': org.name,
            'logo': org.logo or None,
        },
        'table': {
            'id': str(table.id),
            'number': table.table_number,
            'qr_code_id': str(table.qr_code_id),
        },
        'categories': CategorySerializer(categories, many=True).data,
        'menu': MenuListSerializer(menu_items, many=True).data,
    })
