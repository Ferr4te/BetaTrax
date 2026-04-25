from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command
from rest_framework.test import APIClient
from django_tenants.utils import tenant_context

from customers.models import Client as Tenant, Domain
from BetaTrax.models import Product, BetaTester

class TenantFilteringTest(TestCase):
    def setUp(self):
        # Create tenants
        self.tenant1 = Tenant.objects.create(
            schema_name='test_tenant1',
            name='Tenant 1'
        )
        self.tenant2 = Tenant.objects.create(
            schema_name='test_tenant2',
            name='Tenant 2'
        )

        # Run migrations inside the newly created tenant schemas
        call_command('migrate_schemas')   # applies to all tenants

        # Domain mappings
        Domain.objects.create(domain='tenant1.localhost', tenant=self.tenant1)
        Domain.objects.create(domain='tenant2.localhost', tenant=self.tenant2)

        # Create users and related objects 
        with tenant_context(self.tenant1):
            user1 = User.objects.create_user('tester1', password='testpass')
            self.tester1 = BetaTester.objects.create(user=user1, email='tester1@example.com')
            self.product1 = Product.objects.create(name='Product 1')
            self.client1 = APIClient(HTTP_HOST='tenant1.localhost')
            self.client1.force_login(user1)

        with tenant_context(self.tenant2):
            user2 = User.objects.create_user('tester2', password='testpass')
            self.tester2 = BetaTester.objects.create(user=user2, email='tester2@example.com')
            self.product2 = Product.objects.create(name='Product 2')
            self.client2 = APIClient(HTTP_HOST='tenant2.localhost')
            self.client2.force_login(user2)

    def test_defect_isolation_between_tenants(self):
        # Create a defect under tenant1
        data = {
            'version': '1.0',
            'title': 'Crash on login',
            'description': 'App crashes when user logs in.',
            'reproduce_step': 'Open app, enter credentials, click login.',
            'product': self.product1.id,
            'betatester': self.tester1.id,
            'tester_email': 'test@example.com',
        }
        response = self.client1.post('/api/defects/', data, format='json')
        self.assertEqual(response.status_code, 201)  # Created

        # Verify tenant1 sees the defect
        list_response = self.client1.get('/api/defects/new/')
        self.assertEqual(len(list_response.data['results']), 1)

        # Tenant2 should see nothing (empty list)
        list_response2 = self.client2.get('/api/defects/new/')
        self.assertEqual(len(list_response2.data['results']), 0)

        # Trying to access tenant1's defect ID from tenant2 should 404
        defect_id = response.data['id']
        detail_response = self.client2.get(f'/api/defects/{defect_id}/')
        self.assertEqual(detail_response.status_code, 404)