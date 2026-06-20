"""Characterization tests for multi-tenant data isolation.

These lock the *observable behaviour* of tenant scoping through the ViewSet
interface (DRF views), so the seam can be refactored without changing what
callers see. Test the rule, not the implementation:

  - super_admin sees every organization's rows
  - staff see only their own organization's rows
  - cross-organization objects are invisible (404), never leaked
  - writes are forced onto the actor's organization

Run: python manage.py test apps.organizations.tests.test_tenant_isolation
"""
from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.organizations.models import Organization
from apps.users.models import UserProfile
from apps.menu.models import Category, Menu
from apps.menu.views import MenuViewSet
from apps.organizations.views import OrganizationViewSet


def make_org(name):
    return Organization.objects.create(name=name)


def make_staff(org, role='manager', full_name='Staff'):
    user = User.objects.create(username=f'{role}-{org.name}-{full_name}')
    UserProfile.objects.create(user=user, organization=org, role=role, full_name=full_name)
    return user


def make_super_admin():
    user = User.objects.create(username='root')
    UserProfile.objects.create(user=user, organization=None, role='super_admin', full_name='Root')
    return user


def make_menu_item(org, name, price=1000):
    cat = Category.objects.create(organization=org, name=f'cat-{name}')
    return Menu.objects.create(organization=org, category=cat, name=name, price=price)


class TenantIsolationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org_a = make_org('Restaurant A')
        cls.org_b = make_org('Restaurant B')
        cls.item_a = make_menu_item(cls.org_a, 'Plov')
        cls.item_b = make_menu_item(cls.org_b, 'Lagman')
        cls.manager_a = make_staff(cls.org_a, role='manager')
        cls.root = make_super_admin()
        cls.factory = APIRequestFactory()

    def _list_menu_as(self, user):
        view = MenuViewSet.as_view({'get': 'list'})
        request = self.factory.get('/api/menu/')
        if user is not None:
            force_authenticate(request, user=user)
        response = view(request)
        response.render()
        return response

    def _menu_names(self, response):
        data = response.data
        results = data['results'] if isinstance(data, dict) and 'results' in data else data
        return {row['name'] for row in results}

    # --- list scoping -----------------------------------------------------
    def test_staff_sees_only_their_own_organizations_menu(self):
        response = self._list_menu_as(self.manager_a)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._menu_names(response), {'Plov'})

    def test_super_admin_sees_every_organizations_menu(self):
        response = self._list_menu_as(self.root)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._menu_names(response), {'Plov', 'Lagman'})

    def test_anonymous_cannot_list_menu(self):
        response = self._list_menu_as(None)
        self.assertIn(response.status_code, (401, 403))

    # --- object scoping ---------------------------------------------------
    def test_staff_cannot_retrieve_another_organizations_item(self):
        view = MenuViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get('/api/menu/')
        force_authenticate(request, user=self.manager_a)
        response = view(request, pk=str(self.item_b.id))
        self.assertEqual(response.status_code, 404)

    def test_staff_can_retrieve_own_organizations_item(self):
        view = MenuViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get('/api/menu/')
        force_authenticate(request, user=self.manager_a)
        response = view(request, pk=str(self.item_a.id))
        self.assertEqual(response.status_code, 200)

    # --- write scoping ----------------------------------------------------
    def test_create_forces_actors_organization_even_if_another_is_supplied(self):
        cat_a = Category.objects.get(organization=self.org_a)
        view = MenuViewSet.as_view({'post': 'create'})
        request = self.factory.post('/api/menu/', {
            'name': 'Manti',
            'price': 2000,
            'category': str(cat_a.id),
            'organization': str(self.org_b.id),  # attempt to plant into org B
        }, format='json')
        force_authenticate(request, user=self.manager_a)
        response = view(request)
        self.assertEqual(response.status_code, 201, response.data)
        created = Menu.objects.get(name='Manti')
        self.assertEqual(created.organization_id, self.org_a.id)


class OrganizationScopingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org_a = make_org('Restaurant A')
        cls.org_b = make_org('Restaurant B')
        cls.manager_a = make_staff(cls.org_a, role='manager')
        cls.root = make_super_admin()
        cls.factory = APIRequestFactory()

    def _list_orgs_as(self, user):
        view = OrganizationViewSet.as_view({'get': 'list'})
        request = self.factory.get('/api/organizations/')
        force_authenticate(request, user=user)
        response = view(request)
        response.render()
        data = response.data
        results = data['results'] if isinstance(data, dict) and 'results' in data else data
        return response, {row['name'] for row in results}

    def test_manager_sees_only_their_own_organization(self):
        response, names = self._list_orgs_as(self.manager_a)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(names, {'Restaurant A'})

    def test_super_admin_sees_all_organizations(self):
        response, names = self._list_orgs_as(self.root)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(names, {'Restaurant A', 'Restaurant B'})
