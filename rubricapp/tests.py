from rubricapp.models import Semester
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

class SemesterModelTest(TestCase):
	
	def test_model_for_semesters(self):
		first_semester = Semester()
		first_semester.text = '201530'
		first_semester.save()

		second_semester = Semester()
		second_semester.text = '201610'
		second_semester.save()

		saved_items = Semester.objects.all()
		self.assertEqual(saved_items.count(), 2)

		first_saved_semester = saved_items[0]
		second_saved_semester = saved_items[1]
		self.assertEqual(first_saved_semester.text, '201530')
		self.assertEqual(second_saved_semester.text, '201610')
