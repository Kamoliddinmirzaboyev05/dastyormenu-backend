"""Custom permission classes."""
from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """Allow access only to super admins."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'userprofile') and
            request.user.userprofile.role == 'super_admin'
        )


class IsManagerOrAbove(permissions.BasePermission):
    """Allow access to managers and super admins."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'userprofile') and
            request.user.userprofile.role in ['super_admin', 'manager']
        )


class IsChefOrAbove(permissions.BasePermission):
    """Allow access to chefs, managers, and super admins."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'userprofile') and
            request.user.userprofile.role in ['super_admin', 'manager', 'chef']
        )


class IsWaiterOrAbove(permissions.BasePermission):
    """Allow access to all authenticated staff."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'userprofile') and
            request.user.userprofile.is_active
        )


class IsOwnOrganization(permissions.BasePermission):
    """Ensure user can only access their own organization's data.

    Delegates to :class:`apps.organizations.scoping.TenantScope` so the object
    check uses the same rule as queryset scoping and writes.
    """

    def has_object_permission(self, request, view, obj):
        from apps.organizations.scoping import TenantScope
        return TenantScope.can_access(request.user, obj)
