# python manage.py shell
# setup user for demo 

from django_tenants.utils import tenant_context
from django.contrib.auth.models import User
from customers.models import Client as Tenant
from BetaTrax.models import Product, BetaTester, ProductOwner, Developer

tenant1 = Tenant.objects.get(schema_name='tenant1')

with tenant_context(tenant1):
    product = Product.objects.create(name='DemoApp1')
    
    # Tester (superuser)
    t_user = User.objects.create_user('tester1', password='testpass')
    t_user.is_staff = True
    t_user.is_superuser = True
    t_user.save()
    BetaTester.objects.create(user=t_user, email='tester1@gmail.com')
    
    # Product Owner (superuser)
    po_user = User.objects.create_user('owner1', password='testpass')
    po_user.is_staff = True
    po_user.is_superuser = True
    po_user.save()
    ProductOwner.objects.create(user=po_user, product=product)
    
    # Developer (superuser)
    dev_user = User.objects.create_user('dev1', password='testpass')
    dev_user.is_staff = True
    dev_user.is_superuser = True
    dev_user.save()
    Developer.objects.create(user=dev_user, product=product)



tenant2 = Tenant.objects.get(schema_name='tenant2')

with tenant_context(tenant2):
    product = Product.objects.create(name='DemoApp2')
    
    # Tester (superuser)
    t_user = User.objects.create_user('tester2', password='testpass')
    t_user.is_staff = True
    t_user.is_superuser = True
    t_user.save()
    BetaTester.objects.create(user=t_user, email='tester2@gmail.com')
    
    # Product Owner (superuser)
    po_user = User.objects.create_user('owner2', password='testpass')
    po_user.is_staff = True
    po_user.is_superuser = True
    po_user.save()
    ProductOwner.objects.create(user=po_user, product=product)
    
    # Developer (superuser)
    dev_user = User.objects.create_user('dev2', password='testpass')
    dev_user.is_staff = True
    dev_user.is_superuser = True
    dev_user.save()
    Developer.objects.create(user=dev_user, product=product)

exit()

