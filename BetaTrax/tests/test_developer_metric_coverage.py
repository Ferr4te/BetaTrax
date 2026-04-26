from django_tenants.test.cases import TenantTestCase
from django_tenants.utils import tenant_context
from BetaTrax.models import Developer, DefectReport, Product, BetaTester
from django.contrib.auth.models import User