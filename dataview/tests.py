from django.test import TestCase
from unittest import skip
from django.core.urlresolvers import resolve
from dataview.views import home_page, student_view, student_data_view
from rubricapp.models import Semester, Student, Enrollment, EdClasses, Rubric, Row
from django.http import HttpRequest

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
		semester = Semester.objects.create(text="201530")
		semester2 = Semester.objects.create(text="201610")
		edclass1 = EdClasses.objects.create(name="EG 5000")
		edclass2 = EdClasses.objects.create(name="EG 6000")
		semester.classes.add(edclass1)
		semester.classes.add(edclass2)
		
		bob = Student.objects.create(lastname="DaBuilder", firstname="Bob",lnumber="21743148")
		jane = Student.objects.create(lastname="Doe", firstname="Jane",lnumber="21743149")
		jake = Student.objects.create(lastname="The Snake", firstname="Jake", lnumber="0000")
		
		bobenrollment = Enrollment.objects.create(student=bob, edclass=edclass1, semester=semester)
		bobenrollment1 = Enrollment.objects.create(student=bob, edclass=edclass2, semester=semester)
		janeenrollment = Enrollment.objects.create(student=jane, edclass=edclass1, semester=semester)
		janeenrollment2 = Enrollment.objects.create(student=jane, edclass=edclass2, semester=semester)
		writingrubric = Rubric.objects.create(name="writingrubric")

		row1 = Row.objects.create(excellenttext="THE BEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)
								  
		row2 = Row.objects.create(excellenttext="THE GREATEST!",
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)
		
		#Many to many relationship must be added after creation of objects
		#because the manyto-many relationship is not a column in the database
		edclass1.keyrubric.add(writingrubric)
		edclass2.keyrubric.add(writingrubric)
		
		completedrubricforbob = Rubric.objects.create(name="bobcompletedrubric", template=False)
		row1 = Row.objects.create(excellenttext="THE BEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=completedrubricforbob, row_choice=1)
								  
		row2 = Row.objects.create(excellenttext="THE GREATEST!",
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=completedrubricforbob, row_choice=1)
		
		bobenrollment.completedrubric = completedrubricforbob
		bobenrollment.save()
		
		
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
		self.assertIn("Bob DaBuilder", response.content.decode())
		
	def test_student_page_has_submit_button(self):
		response = self.client.get("/data/student/")
		self.assertIn("Submit", response.content.decode())
		
	def test_student_page_can_take_post_request(self):
		request = HttpRequest()
		request.method = "POST"
		request.POST['studentnames'] = "Bob Dabuilder"
		response = student_view(request)
		self.assertEqual(response.status_code, 302)
		
	def test_student_page_redirects_to_individual_student_page(self):
		request = HttpRequest()
		request.method = "POST"
		request.POST['studentnames'] = "21743148"
		response = student_view(request)
		self.assertEqual(response['location'], '21743148/')
	
	def test_dataview_page_exists_for_bob(self):
		response = self.client.get('/data/student/21743148/')
		self.assertIn("Bob", response.content.decode())
		
	def test_data_view_shows_rubrics(self):
		response = self.client.get('/data/student/21743148/')
		self.assertIn("bobcompletedrubric", response.content.decode())
		
	def test_student_page_has_submit_button(self):
		response = self.client.get("/data/student/21743148/")
		self.assertIn("Submit", response.content.decode())
		
	def test_student_data_view_takes_post_request(self):
		request = HttpRequest()
		request.method = "POST"
		request.POST['rubricname'] ="bobcompletedrubric"
		response = student_data_view(request,lnumber="21743148")
		self.assertEqual(response.status_code, 302)
	
	def test_student_data_view_takes_post_request(self):
		request = HttpRequest()
		request.method = "POST"
		request.POST['rubricname'] = "bobcompletedrubric"
		response = student_data_view(request, lnumber="21743148")
		self.assertEqual(response['location'], 'bobcompletedrubric/')
	
