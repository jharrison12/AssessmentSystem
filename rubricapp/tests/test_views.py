from unittest import skip
from rubricapp.models import Semester, EdClasses, Student, Enrollment, Rubric, Row
from django.template.loader import render_to_string
from django.http import HttpRequest
from django.test import TestCase
from rubricapp.views import home_page, semester_page, student_page, rubric_page
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
		edclass1 = EdClasses.objects.create(name="EG 5000")
		semester.classes.add(edclass1)
		
		response = self.client.get('/'+semester.text+'/')

		self.assertContains(response, 'EG 5000') 
	
	def create_two_classes_for_unit_tests(self):
		semester = Semester.objects.get(text="201530")
		class1 = EdClasses.objects.create(name="EG 5000")
		class2 = EdClasses.objects.create(name="EG 6000")
		semester.classes.add(class1)
		semester.classes.add(class2)
		
	def create_two_semesters_for_unit_tests(self):
		Semester.objects.create(text="201530")
		Semester.objects.create(text="201610")
		
	def test_displays_two_classes(self):
		self.create_two_semesters_for_unit_tests()
		self.create_two_classes_for_unit_tests()
		semester = Semester.objects.get(text="201530")
		response = self.client.get('/'+ semester.text +'/')
		self.assertContains(response, "EG 6000")
		self.assertContains(response, "EG 5000")
		
	def test_semester_view_returns_correct_templates(self):
		self.create_two_semesters_for_unit_tests()
		self.create_two_classes_for_unit_tests()
		semester = Semester.objects.get(text="201530")
		response = self.client.get('/'+ semester.text +'/')
		self.assertTemplateUsed(response, 'semester.html')
		
	def test_home_page_can_visit_201610_in_url(self):
		self.create_two_semesters_for_unit_tests()
		request = HttpRequest()
		request.method = 'POST'
		semester = Semester.objects.get(text="201610")
		request.POST['semester'] = semester.text

		response = home_page(request)
		
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/201610/')	
	
	def test_semester_page_can_take_post_request(self):
		self.create_two_semesters_for_unit_tests()
		self.create_two_classes_for_unit_tests()
		request = HttpRequest()
		request.method = "POST"
		edClass = EdClasses.objects.get(name="EG 5000")
		request.POST['edClass'] = edClass.name

		response = semester_page(request, "201530")

		self.assertEqual(response.status_code, 302)

class ClassViewTest(TestCase):

	def add_two_classes_to_semester_add_two_students_to_class(self):
		first_semester = Semester.objects.create(text='201530')
		edClass = EdClasses.objects.create(name='EG 5000') 
		edClass2 = EdClasses.objects.create(name='EG 6000')
		
		first_semester.classes.add(edClass)
		first_semester.classes.add(edClass2)
		
		
		bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
		jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")
		bobenrollment = Enrollment.objects.create(student=bob, edclass=edClass, grade="Excellent")
		janeenrollment = Enrollment.objects.create(student=jane,edclass=edClass)
		bobenrollment2 = Enrollment.objects.create(student=bob,edclass=edClass2)
		janeenrollment2 = Enrollment.objects.create(student=jane,edclass=edClass2)
	
	
	def create_two_semesters_for_unit_tests(self):
		Semester.objects.create(text="201530")
		Semester.objects.create(text="201610")

	
	def test_student_page_returns_correct_template(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		response = self.client.get("/201530/EG5000/")
		self.assertTemplateUsed(response, 'student.html')
		
	def test_semester_page_redirects_to_class_url(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		request = HttpRequest()
		request.method = "POST"
		edClass = EdClasses.objects.get(name="EG 5000")
		request.POST['edClass'] = edClass.name

		response = semester_page(request, "201530")
		
		self.assertEqual(response['location'], 'EG5000/')
	
	def test_semester_page_can_show_without_redirecting(self):
		#TODO setup semester/class/ url
		self.add_two_classes_to_semester_add_two_students_to_class()
		response = self.client.get("/201530/EG5000/")

		self.assertContains(response, 'Bob DaBuilder')
	
	def test_class_page_can_take_post_request(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		request = HttpRequest()
		request.method = "POST"
		bob = Student.objects.get(lnumber="21743148")
		request.POST['studentnames'] = bob.lnumber

		response = student_page(request, "/EG5000/", "201530")

		self.assertEqual(response.status_code, 302)
		
	def test_class_page_redirects_to_student_url(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		request = HttpRequest()
		request.method = 'POST'
		student = Student.objects.get(lnumber="21743148")
		request.POST['studentnames'] = student.lnumber

		response = student_page(request, "/EG5000/", "201530")
		
		self.assertEqual(response.status_code, 302)
		
		self.assertEqual(response['location'], '21743148/')	

class StudentandRubricViewTest(TestCase):

	def add_two_classes_to_semester_add_two_students_to_class_add_one_row(self):
		semester = Semester.objects.create(text="201530")
		edclass1 = EdClasses.objects.create(name="EG 5000")
		edclass2 = EdClasses.objects.create(name="EG 6000")
		semester.classes.add(edclass1)
		semester.classes.add(edclass2)
		
		bob = Student.objects.create(lastname="DaBuilder", firstname="Bob",lnumber="21743148")
		jane = Student.objects.create(lastname="Doe", firstname="Jane",lnumber="21743149")
		
		bobenrollment = Enrollment.objects.create(student=bob, edclass=edclass1)
		bobenrollment1 = Enrollment.objects.create(student=bob, edclass=edclass2)
		janeenrollment = Enrollment.objects.create(student=jane, edclass=edclass1)
		janeenrollment2 = Enrollment.objects.create(student=jane, edclass=edclass2)
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
		bobenrollment.keyrubric.add(writingrubric)
		janeenrollment.keyrubric.add(writingrubric)
	
	def test_studentandrubric_view_returns_correct_template(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get("/201530/EG5000/21743148/")
		self.assertTemplateUsed(response, 'rubric.html')
		
	def test_student_and_rubric_view_shows_student_name(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get("/201530/EG5000/21743148/")
		self.assertContains(response, "DaBuilder, Bob")
	
	def test_student_and_rubric_view_has_excellent_grade(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get("/201530/EG5000/21743148/")
		self.assertContains(response, "Excellent")
	
	def test_rubric_shows_a_cell_under_excellent(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get("/201530/EG5000/21743148/")
		self.assertContains(response, "THE BEST!")
	#TODO FINISH THE THREE TESTS BELOW
	
	def test_rubric_page_shows_rubric_name(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get("/201530/EG5000/21743148/")
		self.assertContains(response, "Writing Rubric")
	
	@skip
	def test_rubric_page_can_take_post_request(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		request = HttpRequest()
		request.method = "POST"
		response = rubric_page(request, "EG5000", "21743148")

		self.assertEqual(response.status_code, 302)

	@skip
	def test_post_request_does_not_create_new_row(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		request = HttpRequest()
		edClass = EdClasses.objects.get(name='EG 5000') 
		bob = Student.objects.get(lnumber="21743148")
		bobenrollment = Enrollment.objects.get(student=bob, edclass=edClass)
		writingrubric = bobenrollment.keyrubric.get(name="writingrubric")
		
		row = Row.objects.filter(rubric=writingrubric)
		self.assertEqual(row.count(), 1)
		response = self.client.get("/EG5000/21743148/")
		response['id_form-0-row_choice'] = '2'

		self.assertEqual(row.count(), 1)

	@skip
	def test_post_request_updates_correct_model(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		
		edClass = EdClasses.objects.get(name='EG 5000') 
		bob = Student.objects.get(lnumber="21743148")
		bobenrollment = Enrollment.objects.get(student=bob, edclass=edClass)
		writingrubric = bobenrollment.keyrubric.get(name="writingrubric")
		row = Row.objects.get(rubric=writingrubric)
		
		#request = HttpRequest()
		#request.method = 'POST'
		#request.POST['id_form-1-id'] = 2
		#response = rubric_page(request, "EG5000", "21743148")


		response = self.client.get('/EG5000/21743148/', {'id_form-0-row_choice':"2"}, follow=True)
		print(response.content)
		self.assertEqual(row.row_choice, 2)

		


