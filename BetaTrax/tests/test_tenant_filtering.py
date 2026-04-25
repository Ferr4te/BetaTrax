from django_tenants.test.cases import TenantTestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django_tenants.utils import tenant_context, schema_context # Import schema_context

from customers.models import Client as Tenant, Domain
from BetaTrax.models import Product, BetaTester, DefectReport

class TenantFilteringTest(TenantTestCase):
    def setUp(self):
        # TenantTestCase automatically creates self.tenant and self.domain for you.
        # We will use the auto-created one as Tenant 1.
        self.tenant1 = self.tenant 
        
        # We need to create Tenant 2 in the 'public' schema context
        with schema_context('public'):
            self.tenant2 = Tenant.objects.create(
                schema_name='test_tenant2',
                name='Tenant 2'
            )
            Domain.objects.create(domain='tenant2.localhost:8000', tenant=self.tenant2)

        # Create objects for Tenant 1 (The default test tenant)
        with tenant_context(self.tenant1):
            user1 = User.objects.create_user('tester1', password='testpass')
            self.tester1 = BetaTester.objects.create(user=user1, email='tester1@example.com')
            self.product1 = Product.objects.create(name='Product 1')
            self.defect_tenant1 = DefectReport.objects.create(
                version='1.0',
                title='Defect in Tenant1',
                description='Test defect',
                reproduce_step='step',
                product=self.product1,
                betatester=self.tester1,
                status=DefectReport.CurrentStatus.NEW # Ensure status is 'New' for PBI-15
            )
            self.client1 = APIClient()
            self.client1.defaults['HTTP_HOST'] = 'testserver' # TenantTestCase uses 'testserver' by default
            self.client1.force_login(user1)

        # Create objects for Tenant 2
        with tenant_context(self.tenant2):
            user2 = User.objects.create_user('tester2', password='testpass')
            self.tester2 = BetaTester.objects.create(user=user2, email='tester2@example.com')
            self.product2 = Product.objects.create(name='Product 2')
            
            self.client2 = APIClient()
            # No Defect report fot tenant 2
            self.client2.defaults['HTTP_HOST'] = 'tenant2.localhost:8000'
            self.client2.force_login(user2)

    # ========== PBI‑15 ==========
    def test_tenant_filtering(self):
        """PBI-15: Lists and views show only the current tenant's data."""
        # Tenant1 sees its defect
        resp = self.client1.get('/api/defects/', HTTP_HOST='tenant2.localhost')
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['id'], self.defect_tenant1.id)

        # Tenant2 sees an empty list
        resp = self.client2.get('/api/defects/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 0)
    # ========== PBI‑16 ==========
#    def test_cross_tenant_access_prevented(self):
#        """PBI-16: Attempting to access another tenant's data returns 404."""
#        # Tenant2 tries to retrieve tenant1's defect detail
#        resp = self.client2.get(f'/api/defects/{self.defect_tenant1.id}/')
#        self.assertEqual(resp.status_code, 404)

        # (Optional) Also verify modification is blocked
#        patch_resp = self.client2.patch(
#            f'/api/defects/{self.defect_tenant1.id}/',
#            {'status': 'Open'}, format='json'
#        )
#        self.assertEqual(patch_resp.status_code, 404)