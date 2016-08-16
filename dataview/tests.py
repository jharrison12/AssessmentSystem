from django.test import TestCase
from unittest import skip
from django.core.urlresolvers import resolve
from dataview.views import home_page, student_view
from rubricapp.models import Semester, Student, Enrollment, EdClasses

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
		
class StudentView(TestCase):

	def setUp(self):
		first_semester = Semester.objects.create(text='201530')
		edClass = EdClasses.objects.create(name='EG 5000') 
		edClass2 = EdClasses.objects.create(name='EG 6000')
		
		first_semester.classes.add(edClass)
		first_semester.classes.add(edClass2)
		
		
		bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
		jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")
		bobenrollment = Enrollment.objects.create(student=bob, edclass=edClass, semester=first_semester)
		janeenrollment = Enrollment.objects.create(student=jane,edclass=edClass, semester=first_semester)
		bobenrollment2 = Enrollment.objects.create(student=bob,edclass=edClass2, semester=first_semester)
		janeenrollment2 = Enrollment.objects.create(student=jane,edclass=edClass2, semester=first_semester)

	def test_student_view_uses_student_view_function(self):
		found = resolve('/data/student/')
		self.assertEqual(found.func, student_view)
	
	def test_student_view_works(self):
		response = self.client.get('/data/student/')
		self.assertContains(response, "Choose a student!")
		
	def test_student_view_uses_correct_template(self):
		response = self.client.get('/data/student/')
		self.assertTemplateUsed(response, 'dataview/studentview.html')
		
	def test_student_page_shows_all_students(self):
		#follow=True follows the redirect to the login page
		response = self.client.get("/data/student/")
		self.assertIn("DaBuilder, Bob", response.content.decode())
