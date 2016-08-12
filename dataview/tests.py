from django.test import TestCase
from unittest import skip
from django.core.urlresolvers import resolve
from dataview.views import home_page

# Create your tests here.

class DataViewHome(TestCase):
	@skip
	def test_data_view_home(self):
		response
		self.assertEqual(found.func, home_page)
		
	def test_data_view_home(self):
		response = self.client.get('data/')
		self.assertEqual(response.content.decode(), '')
		
	def test_data_view_home_uses_template(self):
		response = self.client.get('data/')
		self.assertTemplateUse(respone, 'dataviewhome.html')
