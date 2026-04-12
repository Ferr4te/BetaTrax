from django.test import TestCase

# Create your tests here.
import json

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
import json

from .models import BetaTester, DefectReport, Developer, Product, ProductOwner, Comment


class SprintOnePBITests(TestCase):
	def setUp(self):
	# CREATE USERS FIRST
		self.tester_user = User.objects.create_user(username='tester1', password='pass123')
		self.po_user = User.objects.create_user(username='po1', password='pass123')
		self.dev_user = User.objects.create_user(username='dev1', password='pass123')

		self.product = Product.objects.create()
		self.tester = BetaTester.objects.create(user=self.tester_user, email='tester@example.com')
		self.owner = ProductOwner.objects.create(user=self.po_user, product=self.product)
		self.developer = Developer.objects.create(user=self.dev_user, product=self.product)

	def create_new_defect(self, **overrides):
		defaults = {
			'title': 'Login issue',
			'description': 'Cannot login with valid password',
			'reproduce_step': 'Open app; login with valid account',
			'version': '1.0.0',
			'product': self.product,
			'betatester': self.tester,
			'productowner':self.owner
		}
		defaults.update(overrides)
		return DefectReport.objects.create(**defaults)

	def test_pbi_01_submit_defect_report_with_optional_email(self):
		payload = {
			'title': 'Crash on launch',
			'description': 'App crashes on startup',
			'reproduce_step': 'Install app; open app',
			'version': '1.2.3',
			'product': self.product.id,
			'betatester': self.tester.id,
		}

		response = self.client.post(reverse('defect_form'), payload)

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, reverse('defect_success'))

		defect = DefectReport.objects.get(title='Crash on launch')
		self.assertEqual(defect.product_id, self.product.id)
		self.assertEqual(defect.version, '1.2.3')
		self.assertEqual(defect.betatester_id, self.tester.id)
		self.assertEqual(defect.status, DefectReport.CurrentStatus.NEW)
		self.assertFalse(defect.tester_email)

	def test_pbi_02_evaluate_and_accept_defect(self):
		defect = self.create_new_defect()

		page = self.client.get(reverse('owner_defect'))
		self.assertEqual(page.status_code, 200)
		self.assertContains(page, defect.title)

		response = self.client.patch(
			reverse('owner_defect_evaluate', kwargs={'pk': defect.id}),
			data=json.dumps(
				{
					'status': DefectReport.CurrentStatus.OPEN,
					'severity': DefectReport.Severity.MAJOR,
					'priority': DefectReport.Priority.HIGH,
				}
			),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		defect.refresh_from_db()
		self.assertEqual(defect.status, DefectReport.CurrentStatus.OPEN)
		self.assertEqual(defect.severity, DefectReport.Severity.MAJOR)
		self.assertEqual(defect.priority, DefectReport.Priority.HIGH)

	def test_pbi_03_select_defect_to_work_on(self):
		defect = self.create_new_defect(status=DefectReport.CurrentStatus.OPEN)

		dashboard = self.client.get(f"{reverse('developer_dashboard')}?developer_id={self.developer.id}")
		self.assertEqual(dashboard.status_code, 200)
		self.assertContains(dashboard, defect.title)

		response = self.client.post(
			f"{reverse('assign_defect', kwargs={'pk': defect.id})}?developer_id={self.developer.id}"
		)
		self.assertEqual(response.status_code, 302)

		defect.refresh_from_db()
		self.assertEqual(defect.status, DefectReport.CurrentStatus.ASSIGNED)
		self.assertEqual(defect.developer_id, self.developer.id)

	def test_pbi_04_fix_defect_sets_status(self):
		defect = self.create_new_defect(
			status=DefectReport.CurrentStatus.ASSIGNED,
			developer=self.developer,
		)

		response = self.client.patch(reverse('defect-fix', kwargs={'pk': defect.id}))

		self.assertEqual(response.status_code, 200)
		defect.refresh_from_db()
		self.assertEqual(defect.status, DefectReport.CurrentStatus.FIXED)

	def test_pbi_05_close_fixed_defect_as_resolved(self):
		defect = self.create_new_defect(status=DefectReport.CurrentStatus.FIXED)

		response = self.client.patch(reverse('defect-resolve', kwargs={'pk': defect.id}))

		self.assertEqual(response.status_code, 200)
		defect.refresh_from_db()
		self.assertEqual(defect.status, DefectReport.CurrentStatus.RESOLVED)
	
	def test_pbi_07_reject_defect(self):
		defect = self.create_new_defect(status=DefectReport.CurrentStatus.NEW)

		# Login as product owner first
		self.client.force_login(self.po_user)

		response = self.client.patch(
        	reverse('defect-reject', kwargs={'pk': defect.id}),  # Changed from 'defect-reject'
        	data=json.dumps({}),
        	content_type='application/json',
    	)

		self.assertEqual(response.status_code, 200)
		defect.refresh_from_db()
		self.assertEqual(defect.status, DefectReport.CurrentStatus.REJECTED)
		self.assertIsNone(defect.duplicate_of)

	def test_pbi_08_mark_defect_as_duplicate(self):
		original_defect = self.create_new_defect(
            title='Original Bug',
            status=DefectReport.CurrentStatus.OPEN
        )
		duplicate_defect = self.create_new_defect(
            title='Duplicate Bug',
            status=DefectReport.CurrentStatus.NEW
        )
        
		    # Login as product owner first
		self.client.force_login(self.po_user)

		response = self.client.patch(
            reverse('defect-mark-duplicate', kwargs={'pk': duplicate_defect.id}),
            data=json.dumps({
                'status': DefectReport.CurrentStatus.DUPLICATED,
                'duplicate_of': original_defect.id,
            }),
            content_type='application/json',
        )
        
		self.assertEqual(response.status_code, 200)
		duplicate_defect.refresh_from_db()
		self.assertEqual(duplicate_defect.status, DefectReport.CurrentStatus.DUPLICATED)
		self.assertEqual(duplicate_defect.duplicate_of_id, original_defect.id)
	
	def test_pbi_09_register_product(self):
		
		self.client.force_login(self.po_user)
		response = self.client.post(
            reverse('product-list'),
            data=json.dumps({'name': 'Mobile App'}),
            content_type='application/json',
        )
		
		self.assertEqual(response.status_code, 201)
		self.assertTrue(Product.objects.filter(name='Mobile App').exists())

	def test_pbi_12_add_comment_to_defect(self):
		defect = self.create_new_defect()
		self.client.force_login(self.po_user)
        
		response = self.client.post(
            reverse('defect-comment-list', kwargs={'defect_pk': defect.id}),
            data=json.dumps({'text': 'This is a critical issue'}),
            content_type='application/json',
        )
        
		self.assertEqual(response.status_code, 201)
		self.assertTrue(Comment.objects.filter(defect=defect, text='This is a critical issue').exists())
    
