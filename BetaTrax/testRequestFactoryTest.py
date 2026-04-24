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
		self.defectreport = DefectReport.objects.create(
			title='Crash on launch', 
			description='App crashes on startup',
			reproduce_step='Install app; open app',
			version='1.2.3',
			product=self.product.id,
			betatester=self.tester.id
		)
		self.tester = BetaTester.objects.create(user=self.tester_user, email='tester@example.com')
		self.owner = ProductOwner.objects.create(user=self.po_user, product=self.product)
		self.developer = Developer.objects.create(user=self.dev_user, product=self.product)

	def test_pbi_06_list_defectreport(self):
		request = self.factory.get(reverse('defect-list'))
		view = DefectReportViewSet.as_view({'get': 'list'})
		response = view(request)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertContains(response, 'Crash on launch')
