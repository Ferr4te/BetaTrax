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
