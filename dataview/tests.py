from django.test import TestCase
from django.core.urlresolvers import resolve
from dataview.views import home_page

# Create your tests here.

class DataViewHome(TestCase):
	
	def test_data_view_home(self):
		found = resolve('/')
		self.assertEqual(found.func, home_page)
