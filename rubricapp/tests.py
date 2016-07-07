from unittest import skip
from rubricapp.models import Semester, EdClasses
from django.template.loader import render_to_string
from django.http import HttpRequest
from django.test import TestCase
from rubricapp.views import home_page
from django.core.urlresolvers import resolve

class HomePageTest(TestCase):
	maxDiff = None

	def create_two_semesters_for_unit_tests(self):
		Semester.objects.create(text="201530")
		Semester.objects.create(text="201610")
	
	def test_home_url_resolves_to_home_page_view(self):
		found = resolve('/')
		self.assertEqual(found.func, home_page) 
	
	def test_home_page_returns_correct_html(self):
		request = HttpRequest()
		response = home_page(request)
		semesters = Semester.objects.all()
		expected_html = render_to_string('home.html', { 'semestercode': semesters })
		self.assertMultiLineEqual(response.content.decode(), expected_html)

	
	def test_home_page_can_redirects_after_Post_request(self):
		self.create_two_semesters_for_unit_tests()
		request = HttpRequest()
		request.method = 'POST'
		semester = Semester.objects.get(text="201530")
		request.POST['semester'] = semester.text

		response = home_page(request)
		
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/201530/')
		
	def test_home_page_shows_two_semesters(self):
		self.create_two_semesters_for_unit_tests()
		request = HttpRequest()
		response = home_page(request)
		self.assertEqual(Semester.objects.count(), 2)

	def test_home_page_template_has_two_semesters(self):
		self.create_two_semesters_for_unit_tests()
		request = HttpRequest()
		response = home_page(request)
		self.assertIn('201530', response.content.decode())
		self.assertIn('201610', response.content.decode())

class SemesterClassViewTest(TestCase):
	
	def test_displays_all_classes(self):
		semester = Semester.objects.create(text="201530")
		EdClasses.objects.create(name="EG 5000", semester=semester)

		response = self.client.get('/'+semester.text+'/')

		self.assertContains(response, 'EG 5000') 
	
	def create_two_classes_for_unit_tests(self):
		semester = Semester.objects.get(text="201530")
		EdClasses.objects.create(name="EG 5000", semester=semester)
		EdClasses.objects.create(name="EG 6000", semester=semester)
	
	def create_two_semesters_for_unit_tests(self):
		Semester.objects.create(text="201530")
		Semester.objects.create(text="201610")
		
	def test_displays_two_classes(self):
		self.create_two_semesters_for_unit_tests()
		self.create_two_classes_for_unit_tests()
		semester = Semester.objects.get(text="201530")
		response = self.client.get('/'+ semester.text +'/')
		self.assertContains(response, "EG 6000")
		
	def test_home_page_can_visit_201610_in_url(self):
		self.create_two_semesters_for_unit_tests()
		request = HttpRequest()
		request.method = 'POST'
		semester = Semester.objects.get(text="201610")
		request.POST['semester'] = semester.text

		response = home_page(request)
		
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/201610/')	

class ClassAndSemesterModelTest(TestCase):
	
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
	
	def test_model_for_classes(self):
		first_semester = Semester.objects.create(text='201530')
		EdClasses.objects.create(name='EG 5000', semester=first_semester)
		EdClasses.objects.create(name='EG 6000', semester=first_semester)

		saved_classes = EdClasses.objects.all()
		self.assertEqual(saved_classes.count(), 2)

		first_saved_class = saved_classes[0]
		second_saved_class = saved_classes[1]

		self.assertEqual(first_saved_class.name, 'EG 5000')
		self.assertEqual(second_saved_class.name, 'EG 6000')
	
	def test_classes_link_to_semester(self):
		first_semester = Semester.objects.create(text='201530')
		edClass = EdClasses.objects.create(name='EG 5000', semester=first_semester)
		edClass2 = EdClasses.objects.create(name='EG 6000', semester=first_semester)

		edClass.semester = first_semester
		edClass.save()
		
		edClass2.semester = first_semester
		edClass2.save()
		
		saved_classes = EdClasses.objects.all()
		first_saved_class = saved_classes[0]
		second_saved_class = saved_classes[1]

		self.assertEqual(first_saved_class.semester, first_semester)
		self.assertEqual(second_saved_class.semester, first_semester)
