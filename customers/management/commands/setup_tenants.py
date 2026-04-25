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
        self.stdout.write(self.style.SUCCESS('Tenants and domain mapping created.'))