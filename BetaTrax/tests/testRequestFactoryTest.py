from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
import json
from BetaTrax.views import DefectReportViewSet, ProductViewSet, CommentViewSet, DeveloperViewSet
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

	# GET /api/defects/
	def test_pbi_06_list_defectreport(self):
		request = self.factory.get('/api/defects/') #(reverse('defect-list'))??
		view = DefectReportViewSet.as_view({'get': 'list'})
		response = view(request)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(len(response.data['results']), 1)
		self.assertIn('Crash on launch', str(response.data))

	# GET /api/defects/{id}/
	def test_pbi_06_retrieve_defectreportdetail(self):
		request = self.factory.get(f'/api/defects/{self.defectreport.id}/')
		view = DefectReportViewSet.as_view({'get': 'retrieve'})
		response = view(request, pk=self.defectreport.id)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['id'], self.defectreport.id)
		self.assertEqual(response.data['title'], 'Crash on launch')
		
	# POST /api/defects/
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

	# PATCH /api/defects/{id}/
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
		
	# Product endpoints Start
	# GET /api/products/
	def test_product_list(self):
		request = self.factory.get('/api/products/')
		force_authenticate(request, user=self.po_user)
		view = ProductViewSet.as_view({'get': 'list'})
		response = view(request)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(len(response.data['results']), 1)
		self.assertEqual(response.data['results'][0]['id'], self.product.id)
		self.assertEqual(response.data['results'][0]['name'], self.product.name)
	
	# POST /api/products/
	def test_product_create(self):
		data = {'name': 'NewProduct'}
		request = self.factory.post('/api/products/', data, format='json')
		force_authenticate(request, user=self.po_user)
		view = ProductViewSet.as_view({'post': 'create'})
		response = view(request)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['name'], 'NewProduct')
		self.assertTrue(Product.objects.filter(name='NewProduct').exists())

	# GET /api/products/{id}/
	def test_product_retrieve(self):
		request = self.factory.get(f'/api/products/{self.product.id}/')
		force_authenticate(request, user=self.po_user)
		view = ProductViewSet.as_view({'get': 'retrieve'})
		response = view(request, pk=self.product.id)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['id'], self.product.id)
		self.assertEqual(response.data['name'], self.product.name)

	# PATCH /api/products/{id}/
	def test_product_update(self):
		data = {'name': 'UpdatedName'}
		request = self.factory.patch(f'/api/products/{self.product.id}/', data, format='json')
		force_authenticate(request, user=self.po_user)
		view = ProductViewSet.as_view({'patch': 'partial_update'})
		response = view(request, pk=self.product.id)

		self.assertEqual(response.status_code, 200)
		self.product.refresh_from_db()
		self.assertEqual(self.product.name, 'UpdatedName')

	# DELETE /api/products/{id}/
	def test_product_delete(self):
		request = self.factory.delete(f'/api/products/{self.product.id}/')
		force_authenticate(request, user=self.po_user)
		view = ProductViewSet.as_view({'delete': 'destroy'})
		response = view(request, pk=self.product.id)

		self.assertEqual(response.status_code, 204)
		self.assertFalse(Product.objects.filter(id=self.product.id).exists())
	# Product endpoints End

	# Defect custom actions Start(assign, fix...)
	# POST /api/defects/{id}/assign/
	def test_assign_defect(self):
		with tenant_context(self.tenant):
			self.defectreport.status = DefectReport.CurrentStatus.OPEN
			self.defectreport.save()
		
		request = self.factory.post(f'/api/defects/{self.defectreport.id}/assign/')
		force_authenticate(request, user=self.dev_user)
		view = DefectReportViewSet.as_view({'post': 'assign'})
		response = view(request, pk=self.defectreport.id)

		self.assertEqual(response.status_code, 200)
		self.assertIn('Assigned successfully', response.data.get('message', ''))
		self.defectreport.refresh_from_db()
		self.assertEqual(self.defectreport.status, DefectReport.CurrentStatus.ASSIGNED)
		self.assertEqual(self.defectreport.developer.id, self.developer.id)
	
	# PATCH /api/defects/{id}/fix/
	def test_fix_defect(self):
		with tenant_context(self.tenant):
			self.defectreport.status = DefectReport.CurrentStatus.ASSIGNED
			self.defectreport.developer = self.developer
			self.defectreport.save()

		request = self.factory.patch(f'/api/defects/{self.defectreport.id}/fix/')
		force_authenticate(request, user=self.dev_user)
		view = DefectReportViewSet.as_view({'patch': 'fix'})
		response = view(request, pk=self.defectreport.id)

		self.assertEqual(response.status_code, 200)
		self.defectreport.refresh_from_db()
		self.assertEqual(self.defectreport.status, DefectReport.CurrentStatus.FIXED)

	# PATCH /api/defects/{id}/resolve/
	def test_resolve_defect(self):
		with tenant_context(self.tenant):
			self.defectreport.status = DefectReport.CurrentStatus.FIXED
			self.defectreport.save()

		request = self.factory.patch(f'/api/defects/{self.defectreport.id}/resolve/')
		force_authenticate(request, user=self.po_user)
		view = DefectReportViewSet.as_view({'patch': 'resolve'})
		response = view(request, pk=self.defectreport.id)

		self.assertEqual(response.status_code, 200)
		self.defectreport.refresh_from_db()
		self.assertEqual(self.defectreport.status, DefectReport.CurrentStatus.RESOLVED)
	
	# PATCH /api/defects/{id}/reject/
	def test_reject_defect(self):
		with tenant_context(self.tenant):
			self.defectreport.status = DefectReport.CurrentStatus.NEW
			self.defectreport.productowner = self.owner
			self.defectreport.save()

		request = self.factory.patch(f'/api/defects/{self.defectreport.id}/reject/')
		force_authenticate(request, user=self.po_user)
		view = DefectReportViewSet.as_view({'patch': 'reject'})
		response = view(request, pk=self.defectreport.id)

		self.assertEqual(response.status_code, 200)
		self.defectreport.refresh_from_db()
		self.assertEqual(self.defectreport.status, DefectReport.CurrentStatus.REJECTED)
	
	# PATCH /api/defects/{id}/mark_duplicate/
	def test_mark_duplicate(self):
		with tenant_context(self.tenant):
			self.defectreport.productowner = self.owner
			self.defectreport.save()
			original = DefectReport.objects.create(
				title='Original', description='x', reproduce_step='x', version='1',
				product=self.product, betatester=self.tester,
				status=DefectReport.CurrentStatus.OPEN
			)
		
		request = self.factory.patch(
			f'/api/defects/{self.defectreport.id}/mark_duplicate/',
			{'duplicate_of': original.id}, format='json'
		)
		force_authenticate(request, user=self.po_user)
		view = DefectReportViewSet.as_view({'patch': 'mark_duplicate'})
		response = view(request, pk=self.defectreport.id)

		self.assertEqual(response.status_code, 200)
		self.defectreport.refresh_from_db()
		self.assertEqual(self.defectreport.status, DefectReport.CurrentStatus.DUPLICATED)
		self.assertEqual(self.defectreport.duplicate_of.id, original.id)

	# PATCH /api/defects/{id}/cannot_reproduce/
	def test_cannot_reproduce(self):
		with tenant_context(self.tenant):
			self.defectreport.status = DefectReport.CurrentStatus.ASSIGNED
			self.defectreport.developer = self.developer
			self.defectreport.save()

		request = self.factory.patch(f'/api/defects/{self.defectreport.id}/cannot_reproduce/')
		force_authenticate(request, user=self.dev_user)
		view = DefectReportViewSet.as_view({'patch': 'cannot_reproduce'})
		response = view(request, pk=self.defectreport.id)

		self.assertEqual(response.status_code, 200)
		self.defectreport.refresh_from_db()
		self.assertEqual(self.defectreport.status, DefectReport.CurrentStatus.CANNOT_REPRODUCE)

	# PATCH /api/defects/{id}/reopen/
	def test_reopen_defect(self):
		with tenant_context(self.tenant):
			self.defectreport.status = DefectReport.CurrentStatus.FIXED
			self.defectreport.save()

		request = self.factory.patch(f'/api/defects/{self.defectreport.id}/reopen/')
		force_authenticate(request, user=self.po_user)
		view = DefectReportViewSet.as_view({'patch': 'reopen'})
		response = view(request, pk=self.defectreport.id)

		self.assertEqual(response.status_code, 200)
		self.defectreport.refresh_from_db()
		self.assertEqual(self.defectreport.status, DefectReport.CurrentStatus.REOPENED)
		self.assertIsNone(self.defectreport.developer)
	# Defect custom actions End

	# Comment endpoints Start
	# GET /api/defects/{id}/comments/
	def test_comment_list(self):
		with tenant_context(self.tenant):
			Comment.objects.create(
				defect=self.defectreport,
				author=self.po_user,
				text='Test comment'
			)

		request = self.factory.get(f'/api/defects/{self.defectreport.id}/comments/')
		force_authenticate(request, user=self.po_user)
		view = CommentViewSet.as_view({'get': 'list'})
		response = view(request, defect_pk=self.defectreport.id)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(len(response.data['results']), 1)
		self.assertEqual(response.data['results'][0]['text'], 'Test comment')

	# POST /api/defects/{id}/comments/
	def test_comment_create(self):
		request = self.factory.post(
			f'/api/defects/{self.defectreport.id}/comments/',
			{'text': 'New comment'}, format='json'
		)
		force_authenticate(request, user=self.po_user)
		view = CommentViewSet.as_view({'post': 'create'})
		response = view(request, defect_pk=self.defectreport.id)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['text'], 'New comment')
		self.assertEqual(response.data['author'], self.po_user.username)
		from BetaTrax.models import Comment
		self.assertTrue(Comment.objects.filter(defect=self.defectreport, text='New comment').exists())
	# Comment endpoints End

	# Developer effectiveness endpoints Start
	# Developer effectiveness endpoints End
