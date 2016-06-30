from django.http import HttpRequest
from django.test import TestCase
from rubricapp.views import home_page
from django.core.urlresolvers import resolve

class HomePageTest(TestCase):
	
	def test_home_url_resolves_to_home_page_view(self):
		found = resolve('/')
		self.assertEqual(found.func, home_page) 
	
	def test_home_page_returns_correct_html(self):
		request = HttpRequest()
		response = home_page(request)
		self.assertTrue(response.content.startswith(b'<html>'))
		self.assertIn(b'<title>Assessment System</title>', response.content)
		self.assertTrue(response.content.endswith(b'</html>'))

	#def test_home_page_contains_assessment_in_title(self):
		
# Create your tests here.
	
