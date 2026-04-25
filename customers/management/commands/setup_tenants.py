from django.core.management.base import BaseCommand
from customers.models import Client, Domain

# Just a quick way to use this sample database structure setup for tenants
# Use python manage.py setup_tenants to create the public tenant and a test tenant with the domain mapping
# Since the public didn't contain any data, so we create the test tenant with the domain mapping to localhost

# python manage.py migrate_schemas --shared for SHARED_APPS
# python manage.py migrate_schemas for TENANT_APPS
class Command(BaseCommand):
    help = 'Create public and test tenants'

    def handle(self, *args, **options):
        # Create public tenant if not exists
        public_tenant, _ = Client.objects.get_or_create(
            schema_name='public',
            defaults={'name': 'Public Tenant'}
        )
        # Create test tenant if not exists
        test_tenant, _ = Client.objects.get_or_create(
            schema_name='tenant1',
            defaults={'name': 'Test Company'}
        )
        # Map localhost to tenant1  (remove old mapping if any)
        Domain.objects.filter(domain='localhost').delete()
        Domain.objects.create(domain='localhost', tenant=test_tenant, is_primary=True)

# One tenant is not enough for the test case (PBI 15,16)
# Below create tenant 2   
# And now all three links should work after running 'python manage.py setup_tenants'
# http://localhost:8000/api/   http://tenant1.localhost:8000/api/  http://tenant2.localhost:8000/api/       
        test_tenant2, _ = Client.objects.get_or_create(
            schema_name='tenant2',
            defaults={'name': 'Test Company 2'}
        )
        # Map subdomains to the tenants
        Domain.objects.get_or_create(
            domain='tenant1.localhost',
            defaults={'tenant': test_tenant, 'is_primary': True}
        )
        Domain.objects.get_or_create(
            domain='tenant2.localhost',
            defaults={'tenant': test_tenant2, 'is_primary': True}
        )

        self.stdout.write(self.style.SUCCESS('Tenants and domain mapping created.'))