from django.template.loader import render_to_string
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
		expected_html = render_to_string('home.html')
		self.assertEqual(response.content.decode(), expected_html)

	def test_home_page_can_save_a_Post_request(self):
		request = HttpRequest()
		request.method = 'POST'
		request.POST['submit'] = '201530' 

		response = home_page(request)
		self.assertIn('201530', response.content.decode())
		expected_html = render_to_string(
			'home.html',
			{'semestercode': '201530'}
			)
		self.assertEqual(response.content.decode(), expected_html)
