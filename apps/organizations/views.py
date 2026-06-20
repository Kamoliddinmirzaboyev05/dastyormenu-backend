"""Organization views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Organization
from .scoping import TenantScope
from .serializers import OrganizationSerializer, OrganizationListSerializer
from apps.users.permissions import IsSuperAdmin, IsManagerOrAbove


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing organizations."""
    
    queryset = Organization.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_permissions(self):
        """Authenticated only. Super admins manage all orgs; managers can
        read/update their own org; create/delete is super-admin only."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsManagerOrAbove()]
        # create/delete and subscription activation are super-admin (billing) only.
        return [IsAuthenticated(), IsSuperAdmin()]

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return OrganizationListSerializer
        return OrganizationSerializer

    def get_queryset(self):
        """Tenant-scoped: super admin sees all; others only their own org."""
        return TenantScope.scope_organizations(Organization.objects.all(), self.request.user)
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Organization name'},
                    'logo_file': {'type': 'string', 'format': 'binary', 'description': 'Logo image file (JPG, PNG, GIF, WebP)'},
                    'address': {'type': 'string', 'description': 'Address'},
                    'phone': {'type': 'string', 'description': 'Phone number'},
                    'subscription_plan': {'type': 'string', 'enum': ['trial', 'basic', 'pro', 'enterprise'], 'description': 'Subscription plan'},
                },
                'required': ['name']
            }
        },
        responses={201: OrganizationSerializer},
        description='Create organization with logo upload to ImgBB'
    )
    def create(self, request, *args, **kwargs):
        """Create organization with logo upload."""
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Organization name'},
                    'logo_file': {'type': 'string', 'format': 'binary', 'description': 'New logo image file (JPG, PNG, GIF, WebP)'},
                    'address': {'type': 'string', 'description': 'Address'},
                    'phone': {'type': 'string', 'description': 'Phone number'},
                    'subscription_plan': {'type': 'string', 'enum': ['trial', 'basic', 'pro', 'enterprise'], 'description': 'Subscription plan'},
                }
            }
        },
        responses={200: OrganizationSerializer},
        description='Update organization with optional new logo upload to ImgBB'
    )
    def update(self, request, *args, **kwargs):
        """Update organization with optional new logo."""
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Organization name'},
                    'logo_file': {'type': 'string', 'format': 'binary', 'description': 'New logo image file (JPG, PNG, GIF, WebP)'},
                    'address': {'type': 'string', 'description': 'Address'},
                    'phone': {'type': 'string', 'description': 'Phone number'},
                    'subscription_plan': {'type': 'string', 'enum': ['trial', 'basic', 'pro', 'enterprise'], 'description': 'Subscription plan'},
                }
            }
        },
        responses={200: OrganizationSerializer},
        description='Partial update organization with optional new logo upload to ImgBB'
    )
    def partial_update(self, request, *args, **kwargs):
        """Partial update organization with optional new logo."""
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description='Subscription activated')},
        description='Activate organization subscription'
    )
    @action(detail=True, methods=['post'])
    def activate_subscription(self, request, pk=None):
        """Activate organization subscription."""
        organization = self.get_object()
        organization.subscription_status = True
        organization.save(update_fields=['subscription_status'])
        return Response({'status': 'subscription activated'})
    
    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description='Subscription deactivated')},
        description='Deactivate organization subscription'
    )
    @action(detail=True, methods=['post'])
    def deactivate_subscription(self, request, pk=None):
        """Deactivate organization subscription."""
        organization = self.get_object()
        organization.subscription_status = False
        organization.save(update_fields=['subscription_status'])
        return Response({'status': 'subscription deactivated'})
