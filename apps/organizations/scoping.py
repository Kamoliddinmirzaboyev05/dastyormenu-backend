"""TenantScope — the single source of truth for multi-tenant isolation.

The whole multi-tenant guarantee of this SaaS is one rule:

  * a ``super_admin`` acts across every organization;
  * any other staff member is confined to their own organization;
  * an actor with no profile sees nothing and may not write.

Before, that rule was re-derived in three shapes — the ``OrganizationMixin``
queryset/create, the ``IsOwnOrganization`` object check, and
``OrganizationViewSet.get_queryset``. Three copies means three places to leak a
tenant. This module states the rule once; every caller crosses this interface
instead of re-implementing it.

The interface is small (scope a queryset, check an object, assign on write); the
implementation absorbs the role logic, the anonymous/no-profile edge cases, and
the organization-vs-self distinction. That makes it the test surface for tenant
isolation — exercise these five methods and you have covered the rule.
"""
from rest_framework.exceptions import PermissionDenied


class TenantScope:
    """One seam for the tenant-isolation rule. Stateless; all classmethods."""

    SUPER_ADMIN = 'super_admin'

    @staticmethod
    def profile(user):
        """The actor's UserProfile, or ``None`` for anonymous / profile-less users."""
        if user is None or not getattr(user, 'is_authenticated', False):
            return None
        return getattr(user, 'userprofile', None)

    @classmethod
    def is_super_admin(cls, user) -> bool:
        profile = cls.profile(user)
        return bool(profile and profile.role == cls.SUPER_ADMIN)

    @classmethod
    def scope(cls, queryset, user, *, org_field='organization'):
        """Confine a queryset of organization-owned rows to what ``user`` may see."""
        profile = cls.profile(user)
        if profile is None:
            return queryset.none()
        if profile.role == cls.SUPER_ADMIN:
            return queryset
        return queryset.filter(**{org_field: profile.organization})

    @classmethod
    def scope_organizations(cls, queryset, user):
        """Confine a queryset *of organizations themselves* (self-scoping).

        Organizations have no ``organization`` FK — staff see only their own row.
        """
        profile = cls.profile(user)
        if profile is None:
            return queryset.none()
        if profile.role == cls.SUPER_ADMIN:
            return queryset
        if profile.organization_id:
            return queryset.filter(id=profile.organization_id)
        return queryset.none()

    @classmethod
    def can_access(cls, user, obj, *, org_attr='organization') -> bool:
        """Object-level check: may ``user`` touch this organization-owned ``obj``?"""
        profile = cls.profile(user)
        if profile is None:
            return False
        if profile.role == cls.SUPER_ADMIN:
            return True
        if hasattr(obj, org_attr):
            return getattr(obj, f'{org_attr}_id') == profile.organization_id
        return False

    @classmethod
    def assign_on_create(cls, serializer, user) -> None:
        """Force the actor's organization onto a write.

        A ``super_admin`` may target another organization by supplying it
        explicitly; everyone else is pinned to their own.
        """
        profile = cls.profile(user)
        if profile is None:
            raise PermissionDenied("User profile not found")
        if profile.role == cls.SUPER_ADMIN:
            if 'organization' not in serializer.validated_data:
                serializer.save(organization=profile.organization)
            else:
                serializer.save()
        else:
            serializer.save(organization=profile.organization)
