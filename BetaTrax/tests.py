from django.test import TestCase

# Create your tests here.
import json

from django.test import TestCase
from django.urls import reverse

from .models import BetaTester, DefectReport, Developer, Product, ProductOwner


class SprintOnePBITests(TestCase):
	def setUp(self):
		self.product = Product.objects.create()
		self.tester = BetaTester.objects.create(email='tester@example.com')
		self.owner = ProductOwner.objects.create(product=self.product)
		self.developer = Developer.objects.create(product=self.product)

	def create_new_defect(self, **overrides):
		defaults = {
			'title': 'Login issue',
			'description': 'Cannot login with valid password',
			'reproduce_step': 'Open app; login with valid account',
			'version': '1.0.0',
			'product': self.product,
			'betatester': self.tester,
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

		response = self.client.patch(reverse('fix_defect', kwargs={'pk': defect.id}))

		self.assertEqual(response.status_code, 200)
		defect.refresh_from_db()
		self.assertEqual(defect.status, DefectReport.CurrentStatus.FIXED)

	def test_pbi_05_close_fixed_defect_as_resolved(self):
		defect = self.create_new_defect(status=DefectReport.CurrentStatus.FIXED)

		response = self.client.patch(reverse('resolve_defect', kwargs={'pk': defect.id}))

		self.assertEqual(response.status_code, 200)
		defect.refresh_from_db()
		self.assertEqual(defect.status, DefectReport.CurrentStatus.RESOLVED)
