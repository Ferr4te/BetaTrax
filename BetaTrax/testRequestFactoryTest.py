from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
import json
from .views import DefectReportViewSet, ProductViewSet
from .models import BetaTester, DefectReport, Developer, Product, ProductOwner, Comment

class DefectReportViewSetTests(APITestCase):
	def setUp(self):
		self.factory = APIRequestFactory()
		self.tester_user = User.objects.create_user(username='tester1', password='pass123')
		self.po_user = User.objects.create_user(username='po1', password='pass123')
		self.dev_user = User.objects.create_user(username='dev1', password='pass123')
		
		self.product = Product.objects.create()
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

	def test_pbi_06_list_defectreport(self):
		request = self.factory.get('/api/defects/') #(reverse('defect-list'))??
		view = DefectReportViewSet.as_view({'get': 'list'})
		response = view(request)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertIn('Crash on launch', str(response.data))

	def test_pbi_06_retrieve_defectreportdetail(self):
		request = self.factory.get(f'/api/defects/{self.defect.id}/')
		view = DefectReportViewSet.as_view({'get': 'retrieve'})
		response = view(request, pk=self.defect.id)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		# need add
		
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

	def test_pbi_02_update_defectreport(self):
		data = {
			'status': DefectReport.CurrentStatus.OPEN,
			'severity': DefectReport.Severity.MAJOR,
			'priority': DefectReport.Priority.HIGH,
		}
		request = self.factory.put(f'/api/defects/{self.defect.id}/', data, format='json')
		view = DefectReportViewSet.as_view({'put': 'update'})
		response = view(request, pk=self.defectreport.id)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		# need add
		
