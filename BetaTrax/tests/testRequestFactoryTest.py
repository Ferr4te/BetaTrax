from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
import json
from BetaTrax.views import DefectReportViewSet, ProductViewSet
from BetaTrax.models import BetaTester, DefectReport, Developer, Product, ProductOwner, Comment
from django_tenants.test.cases import TenantTestCase
from django_tenants.utils import tenant_context
from django.db import connection
from customers.models import Client as Tenant, Domain
from rest_framework.test import force_authenticate


class DefectReportViewSetTests(TenantTestCase):
	def setUp(self):
		super().setUp()
		with tenant_context(self.tenant):
			self.tester_user = User.objects.create_user(username='tester1', password='pass123')
			self.po_user = User.objects.create_user(username='po1', password='pass123')
			self.dev_user = User.objects.create_user(username='dev1', password='pass123')

			self.product = Product.objects.create(name='Test Product')
			self.tester = BetaTester.objects.create(user=self.tester_user, email='tester@example.com')
			self.owner = ProductOwner.objects.create(user=self.po_user, product=self.product)
			self.developer = Developer.objects.create(user=self.dev_user, product=self.product)
			self.defectreport = DefectReport.objects.create(
				title='Crash on launch',
				description='App crashes on startup',
				reproduce_step='Install app; open app',
				version='1.2.3',
				product=self.product,
				betatester=self.tester
			)
		connection.set_tenant(self.tenant)
		self.factory = APIRequestFactory()

	def test_pbi_06_list_defectreport(self):
		request = self.factory.get('/api/defects/') #(reverse('defect-list'))??
		view = DefectReportViewSet.as_view({'get': 'list'})
		response = view(request)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(len(response.data['results']), 1)
		self.assertIn('Crash on launch', str(response.data))

	def test_pbi_06_retrieve_defectreportdetail(self):
		request = self.factory.get(f'/api/defects/{self.defectreport.id}/')
		view = DefectReportViewSet.as_view({'get': 'retrieve'})
		response = view(request, pk=self.defectreport.id)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['id'], self.defectreport.id)
		self.assertEqual(response.data['title'], 'Crash on launch')
		
	def test_pbi_01_create_defectreport(self):
		data = {
			'title':'Login issue',
			'description':'Cannot login with valid password',
			'reproduce_step':'Open app; login with valid account',
			'version':'1.0.0',
			'product':self.product.id,
			'betatester':self.tester.id,
		}
		request = self.factory.post('/api/defects/', data, format='json')
		view = DefectReportViewSet.as_view({'post': 'create'})
		response = view(request)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertIn('Login issue', str(response.data))
		self.assertEqual(DefectReport.objects.count(), 2)
		new_defect = DefectReport.objects.get(title='Login issue')
		self.assertEqual(new_defect.version, '1.0.0')

	def test_pbi_02_update_defectreport(self):
		data = {
			'status': DefectReport.CurrentStatus.OPEN,
			'severity': DefectReport.Severity.MAJOR,
			'priority': DefectReport.Priority.HIGH,
		}
		request = self.factory.patch(f'/api/defects/{self.defectreport.id}/', data, format='json')
		view = DefectReportViewSet.as_view({'patch': 'partial_update'})
		response = view(request, pk=self.defectreport.id)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.defectreport.refresh_from_db()
		self.assertEqual(self.defectreport.status, DefectReport.CurrentStatus.OPEN)
		self.assertEqual(self.defectreport.severity, DefectReport.Severity.MAJOR)
		self.assertEqual(self.defectreport.priority, DefectReport.Priority.HIGH)
		
