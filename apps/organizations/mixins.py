"""Tenant-isolation mixin for ViewSets.

Thin adapter over :class:`apps.organizations.scoping.TenantScope`. The rule lives
in ``TenantScope``; this mixin only wires it into DRF's ViewSet lifecycle.
"""
from apps.organizations.scoping import TenantScope


class OrganizationMixin:
    """Scope a ModelViewSet's queryset and writes to the actor's organization."""

    def get_queryset(self):
        return TenantScope.scope(super().get_queryset(), self.request.user)

    def perform_create(self, serializer):
        TenantScope.assign_on_create(serializer, self.request.user)
