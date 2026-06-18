"""Menu views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Category, Menu
from .serializers import CategorySerializer, MenuSerializer, MenuListSerializer
from .mixins import OrganizationMixin
from apps.users.permissions import IsManagerOrAbove


class CategoryViewSet(OrganizationMixin, viewsets.ModelViewSet):
    """ViewSet for managing categories."""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['sort_order', 'name', 'created_at']
    ordering = ['sort_order']
    
    def get_permissions(self):
        """Authenticated staff read their own org; managers write.

        Public (customer) menu access goes through the QR-scoped
        /api/public/menu/ endpoint, NOT this ViewSet.
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]


class MenuViewSet(OrganizationMixin, viewsets.ModelViewSet):
    """ViewSet for managing menu items."""
    
    queryset = Menu.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_available']
    search_fields = ['name', 'description', 'ingredients']
    ordering_fields = ['sort_order', 'name', 'price', 'created_at']
    ordering = ['sort_order']
    
    def get_permissions(self):
        """Authenticated staff read their own org's menu; managers write.

        Public (customer) menu access goes through the QR-scoped
        /api/public/menu/ endpoint, NOT this ViewSet.
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]

    def get_queryset(self):
        """Tenant-scoped via OrganizationMixin; keep category select_related."""
        return super().get_queryset().select_related('category')

    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'list':
            return MenuListSerializer
        return MenuSerializer
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Menu item name'},
                    'description': {'type': 'string', 'description': 'Description'},
                    'price': {'type': 'integer', 'description': 'Price in UZS tiyin'},
                    'category': {'type': 'string', 'format': 'uuid', 'description': 'Category UUID'},
                    'image': {'type': 'string', 'format': 'binary', 'description': 'Image file (JPG, PNG, GIF, WebP)'},
                    'cook_time_minutes': {'type': 'integer', 'description': 'Cooking time in minutes'},
                    'ingredients': {'type': 'string', 'description': 'Ingredients list'},
                    'is_available': {'type': 'boolean', 'description': 'Availability status'},
                    'sort_order': {'type': 'integer', 'description': 'Sort order'},
                },
                'required': ['name', 'price', 'category']
            }
        },
        responses={201: MenuSerializer},
        description='Create menu item with image upload to ImgBB'
    )
    def create(self, request, *args, **kwargs):
        """Create menu item with image upload."""
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Menu item name'},
                    'description': {'type': 'string', 'description': 'Description'},
                    'price': {'type': 'integer', 'description': 'Price in UZS tiyin'},
                    'category': {'type': 'string', 'format': 'uuid', 'description': 'Category UUID'},
                    'image': {'type': 'string', 'format': 'binary', 'description': 'New image file (JPG, PNG, GIF, WebP)'},
                    'cook_time_minutes': {'type': 'integer', 'description': 'Cooking time in minutes'},
                    'ingredients': {'type': 'string', 'description': 'Ingredients list'},
                    'is_available': {'type': 'boolean', 'description': 'Availability status'},
                    'sort_order': {'type': 'integer', 'description': 'Sort order'},
                }
            }
        },
        responses={200: MenuSerializer},
        description='Update menu item with optional new image upload to ImgBB'
    )
    def update(self, request, *args, **kwargs):
        """Update menu item with optional new image."""
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Menu item name'},
                    'description': {'type': 'string', 'description': 'Description'},
                    'price': {'type': 'integer', 'description': 'Price in UZS tiyin'},
                    'category': {'type': 'string', 'format': 'uuid', 'description': 'Category UUID'},
                    'image': {'type': 'string', 'format': 'binary', 'description': 'New image file (JPG, PNG, GIF, WebP)'},
                    'cook_time_minutes': {'type': 'integer', 'description': 'Cooking time in minutes'},
                    'ingredients': {'type': 'string', 'description': 'Ingredients list'},
                    'is_available': {'type': 'boolean', 'description': 'Availability status'},
                    'sort_order': {'type': 'integer', 'description': 'Sort order'},
                }
            }
        },
        responses={200: MenuSerializer},
        description='Partial update menu item with optional new image upload to ImgBB'
    )
    def partial_update(self, request, *args, **kwargs):
        """Partial update menu item with optional new image."""
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description='Availability toggled')},
        description='Toggle menu item availability (stop-list)'
    )
    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, pk=None):
        """Toggle menu item availability (stop-list)."""
        menu_item = self.get_object()
        menu_item.toggle_availability()
        return Response({
            'status': 'availability toggled',
            'is_available': menu_item.is_available
        })
