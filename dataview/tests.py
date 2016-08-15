from django.test import TestCase
from unittest import skip
from django.core.urlresolvers import resolve
from dataview.views import home_page

# Create your tests here.

class DataViewHome(TestCase):

	def test_data_view_home_returns_function(self):
		found = resolve('/data/')
		self.assertEqual(found.func, home_page)
		
	def test_data_view_home(self):
		response = self.client.get('/data/')
		self.assertContains(response, 'You', status_code=200)
		
	def test_data_view_home_uses_template(self):
		response = self.client.get('/data/')
		self.assertTemplateUsed(response, 'dataview/dataviewhome.html')
