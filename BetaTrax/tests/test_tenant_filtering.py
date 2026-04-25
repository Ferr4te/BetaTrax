from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.contrib.auth.models import User
from django_tenants.utils import tenant_context, schema_context

from customers.models import Client as Tenant, Domain
from BetaTrax.models import Product, BetaTester, DefectReport


class TenantFilteringTest(TenantTestCase):
    def setUp(self):
        super().setUp() # creates public schema + test tenant + domain

        # create a second tenant in the public schema
        with schema_context('public'):
            # tenant 1 domain 
            Domain.objects.create(
                domain='tenant1.localhost',
                tenant=self.tenant,
                is_primary=True
            )

            # tenant 2 domain
            self.tenant2 = Tenant.objects.create(
                schema_name='test_tenant2',
                name='Tenant 2'
            )
            Domain.objects.create(
                domain='tenant2.localhost',
                tenant=self.tenant2,
                is_primary=True
            )

        # populate tenant 1 (the auto‑created one) with data
        with tenant_context(self.tenant):
            self.user1 = User.objects.create_user('tester1', password='pass')
            self.tester1 = BetaTester.objects.create(
                user=self.user1, email='tester1@example.com'
            )
            self.product1 = Product.objects.create(name='Product A')
            self.defect_tenant1 = DefectReport.objects.create(
                version='1.0',
                title='Defect in Tenant1',
                description='Test',
                reproduce_step='step',
                product=self.product1,
                betatester=self.tester1,
                status=DefectReport.CurrentStatus.NEW,
            )

        # populate tenant 2 (no defects)
        with tenant_context(self.tenant2):
            self.user2 = User.objects.create_user('tester2', password='pass')
            self.tester2 = BetaTester.objects.create(
                user=self.user2, email='tester2@example.com'
            )
            self.product2 = Product.objects.create(name='Product B')

        # create tenant‑aware clients (using TenantClient makes hostname automatic)
        self.client1 = TenantClient(self.tenant, HTTP_HOST='tenant1.localhost')
        self.client2 = TenantClient(self.tenant2, HTTP_HOST='tenant2.localhost')
        self.client1.force_login(self.user1)
        self.client2.force_login(self.user2)

    # ==================== PBI‑15 ====================
    def test_tenant_filtering(self):
        # Tenant1 sees its defect
        resp = self.client1.get('/api/defects/', {'status': 'New'})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['id'], self.defect_tenant1.id)

        # Tenant2 sees empty list
        resp = self.client2.get('/api/defects/', {'status': 'New'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 0)

