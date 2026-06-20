"""Unit tests for the TenantScope interface — the tenant-isolation rule itself.

These exercise the five public methods directly, covering the edge cases the
HTTP-level tests don't reach (anonymous users, authenticated-but-profile-less
users, staff whose organization is unset).
"""
from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase
from rest_framework.exceptions import PermissionDenied

from apps.organizations.models import Organization
from apps.organizations.scoping import TenantScope
from apps.users.models import UserProfile
from apps.menu.models import Menu, Category


class TenantScopeProfileTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org = Organization.objects.create(name='Org')
        cls.staff_user = User.objects.create(username='staff')
        UserProfile.objects.create(user=cls.staff_user, organization=cls.org,
                                   role='manager', full_name='Manager')
        cls.profileless = User.objects.create(username='ghost')  # authenticated, no profile

    def test_anonymous_has_no_profile(self):
        self.assertIsNone(TenantScope.profile(AnonymousUser()))

    def test_authenticated_user_without_profile_has_no_profile(self):
        self.assertIsNone(TenantScope.profile(self.profileless))

    def test_staff_user_has_profile(self):
        self.assertIsNotNone(TenantScope.profile(self.staff_user))

    def test_is_super_admin_false_for_manager(self):
        self.assertFalse(TenantScope.is_super_admin(self.staff_user))


class TenantScopeQuerysetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org_a = Organization.objects.create(name='A')
        cls.org_b = Organization.objects.create(name='B')
        cat_a = Category.objects.create(organization=cls.org_a, name='ca')
        cat_b = Category.objects.create(organization=cls.org_b, name='cb')
        Menu.objects.create(organization=cls.org_a, category=cat_a, name='a', price=1)
        Menu.objects.create(organization=cls.org_b, category=cat_b, name='b', price=1)

        cls.manager_a = User.objects.create(username='ma')
        UserProfile.objects.create(user=cls.manager_a, organization=cls.org_a,
                                   role='manager', full_name='MA')
        cls.root = User.objects.create(username='root')
        UserProfile.objects.create(user=cls.root, organization=None,
                                   role='super_admin', full_name='Root')
        cls.orphan = User.objects.create(username='orphan')
        UserProfile.objects.create(user=cls.orphan, organization=None,
                                   role='manager', full_name='Orphan')

    def test_scope_confines_staff_to_their_org(self):
        qs = TenantScope.scope(Menu.objects.all(), self.manager_a)
        self.assertEqual({m.name for m in qs}, {'a'})

    def test_scope_returns_everything_for_super_admin(self):
        qs = TenantScope.scope(Menu.objects.all(), self.root)
        self.assertEqual({m.name for m in qs}, {'a', 'b'})

    def test_scope_returns_nothing_for_anonymous(self):
        qs = TenantScope.scope(Menu.objects.all(), AnonymousUser())
        self.assertEqual(list(qs), [])

    def test_scope_organizations_self_scopes_staff(self):
        qs = TenantScope.scope_organizations(Organization.objects.all(), self.manager_a)
        self.assertEqual({o.name for o in qs}, {'A'})

    def test_scope_organizations_returns_all_for_super_admin(self):
        qs = TenantScope.scope_organizations(Organization.objects.all(), self.root)
        self.assertEqual({o.name for o in qs}, {'A', 'B'})

    def test_scope_organizations_returns_nothing_for_orgless_staff(self):
        qs = TenantScope.scope_organizations(Organization.objects.all(), self.orphan)
        self.assertEqual(list(qs), [])


class TenantScopeObjectAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org_a = Organization.objects.create(name='A')
        cls.org_b = Organization.objects.create(name='B')
        cat_a = Category.objects.create(organization=cls.org_a, name='ca')
        cls.item_a = Menu.objects.create(organization=cls.org_a, category=cat_a, name='a', price=1)

        cls.manager_a = User.objects.create(username='ma')
        UserProfile.objects.create(user=cls.manager_a, organization=cls.org_a,
                                   role='manager', full_name='MA')
        cls.manager_b = User.objects.create(username='mb')
        UserProfile.objects.create(user=cls.manager_b, organization=cls.org_b,
                                   role='manager', full_name='MB')
        cls.root = User.objects.create(username='root')
        UserProfile.objects.create(user=cls.root, organization=None,
                                   role='super_admin', full_name='Root')

    def test_owner_can_access(self):
        self.assertTrue(TenantScope.can_access(self.manager_a, self.item_a))

    def test_other_org_cannot_access(self):
        self.assertFalse(TenantScope.can_access(self.manager_b, self.item_a))

    def test_super_admin_can_access_any(self):
        self.assertTrue(TenantScope.can_access(self.root, self.item_a))

    def test_anonymous_cannot_access(self):
        self.assertFalse(TenantScope.can_access(AnonymousUser(), self.item_a))


class TenantScopeAssignOnCreateTests(TestCase):
    def test_profileless_actor_is_refused(self):
        ghost = User.objects.create(username='ghost')
        with self.assertRaises(PermissionDenied):
            TenantScope.assign_on_create(serializer=None, user=ghost)
