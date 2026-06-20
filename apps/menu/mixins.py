"""Back-compat shim.

``OrganizationMixin`` now lives in :mod:`apps.organizations.mixins` (tenant
isolation belongs to the organizations app, not menu). Re-exported here so the
existing ``from apps.menu.mixins import OrganizationMixin`` imports keep working.
"""
from apps.organizations.mixins import OrganizationMixin

__all__ = ['OrganizationMixin']
