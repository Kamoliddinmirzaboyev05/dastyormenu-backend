"""Mixins for tenant isolation."""
from rest_framework.exceptions import PermissionDenied


class OrganizationMixin:
    """Mixin to filter queryset by organization (tenant isolation)."""
    
    def get_queryset(self):
        """Filter queryset by user's organization."""
        queryset = super().get_queryset()
        user = self.request.user
        
        if not hasattr(user, 'userprofile'):
            return queryset.none()
        
        # Super admin can see all
        if user.userprofile.role == 'super_admin':
            return queryset
        
        # Filter by organization
        return queryset.filter(organization=user.userprofile.organization)
    
    def perform_create(self, serializer):
        """Automatically set organization on create."""
        user = self.request.user
        
        if not hasattr(user, 'userprofile'):
            raise PermissionDenied("User profile not found")
        
        # Super admin can set any organization
        if user.userprofile.role == 'super_admin':
            if 'organization' not in serializer.validated_data:
                serializer.save(organization=user.userprofile.organization)
            else:
                serializer.save()
        else:
            # Force user's organization
            serializer.save(organization=user.userprofile.organization)
