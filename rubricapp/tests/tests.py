from unittest import skip
from rubricapp.models import Semester, EdClasses, Student, Enrollment, Rubric, Row
from django.template.loader import render_to_string
from django.http import HttpRequest
from django.test import TestCase
from rubricapp.views import home_page, semester_page, student_page
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
		
		
		bob = Student.objects.create(name="Bob DaBuilder")
		jane = Student.objects.create(name="Jane Doe")

		bobenrollment = Enrollment.objects.create(student=bob, edclass=edClass, grade="Excellent")
		janeenrollment = Enrollment.objects.create(student=jane,edclass=edClass)
		bobenrollment2 = Enrollment.objects.create(student=bob,edclass=edClass2)
		janeenrollment2 = Enrollment.objects.create(student=jane,edclass=edClass2)
	
	
	def create_two_semesters_for_unit_tests(self):
		Semester.objects.create(text="201530")
		Semester.objects.create(text="201610")

	
	def test_student_page_returns_correct_template(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		response = self.client.get("/EG5000/")
		self.assertTemplateUsed(response, 'student.html')
		
	def test_semester_page_redirects_to_class_url(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		request = HttpRequest()
		request.method = "POST"
		edClass = EdClasses.objects.get(name="EG 5000")
		request.POST['edClass'] = edClass.name

		response = semester_page(request, "201530")
		
		self.assertEqual(response['location'], '/EG5000/')
	
	def test_semester_page_can_show_without_redirecting(self):
		#TODO setup semester/class/ url
		self.add_two_classes_to_semester_add_two_students_to_class()
		response = self.client.get("/EG5000/")

		self.assertContains(response, 'Bob DaBuilder')
	
	def test_class_page_can_take_post_request(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		request = HttpRequest()
		request.method = "POST"
		bob = Student.objects.get(name="Bob DaBuilder")
		request.POST['studentnames'] = bob.name

		response = student_page(request, "/EG5000/")

		self.assertEqual(response.status_code, 302)
		
	def test_class_page_redirects_to_student_url(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		request = HttpRequest()
		request.method = 'POST'
		student = Student.objects.get(name="Bob DaBuilder")
		request.POST['studentnames'] = student.name

		response = student_page(request, "/EG5000/")
		
		self.assertEqual(response.status_code, 302)
		
		self.assertEqual(response['location'], 'bobdabuilder/')	

class StudentandRubricViewTest(TestCase):

	def add_two_classes_to_semester_add_two_students_to_class(self):
		first_semester = Semester.objects.create(text='201530')
		edClass = EdClasses.objects.create(name='EG 5000') 
		edClass2 = EdClasses.objects.create(name='EG 6000')
		
		first_semester.classes.add(edClass)
		first_semester.classes.add(edClass2)
		
		
		bob = Student.objects.create(name="Bob DaBuilder")
		jane = Student.objects.create(name="Jane Doe")

		bobenrollment = Enrollment.objects.create(student=bob, edclass=edClass)
		janeenrollment = Enrollment.objects.create(student=jane,edclass=edClass)
		bobenrollment2 = Enrollment.objects.create(student=bob,edclass=edClass2)
		janeenrollment2 = Enrollment.objects.create(student=jane,edclass=edClass2)
	
	def test_studentandrubric_view_returns_correct_template(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		response = self.client.get("/EG5000/bobdabuilder/")
		self.assertTemplateUsed(response, 'rubric.html')
		
	def test_student_and_rubric_view_shows_student_name(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		response = self.client.get("/EG5000/bobdabuilder/")
		self.assertContains(response, "Bob DaBuilder")
	
	def test_student_and_rubric_view_has_excellent_grade(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		response = self.client.get("/EG5000/bobdabuilder/")
		self.assertContains(response, "Excellent")
	
	def test_rubric_shows_a_cell_under_excellent(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		response = self.client.get("/EG5000/bobdabuilder/")
		self.assertContains(response, "Greatest writing ever")

class TestRubricModel(TestCase):
			
	def create_rubric_and_rows_connect_to_class(self):
		first_semester = Semester.objects.create(text='201530')
		edClass = EdClasses.objects.create(name='EG 5000') 
		first_semester.classes.add(edClass)
		writingrubric = Rubric.objects.create(name="writingrubric")
		
		bob = Student.objects.create(name="Bob DaBuilder")
		row1 = Row.objects.create(excellenttext="THE BEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)
	
		
		
		#writingrubric.add(row1)

		bobenrollment = Enrollment.objects.create(student=bob, edclass=edClass)
		bobenrollment.keyrubric.add(writingrubric)
		
	def test_rubric_connected_with_enrollment_class(self):
		self.create_rubric_and_rows_connect_to_class()
		rubrics = Rubric.objects.all()
		self.assertEqual(rubrics.count(), 1)
		

class ClassAndSemesterModelTest(TestCase):
	
	def add_two_classes_to_semester_add_two_students_to_class(self):
		first_semester = Semester.objects.create(text='201530')
		edClass = EdClasses.objects.create(name='EG 5000') 
		edClass2 = EdClasses.objects.create(name='EG 6000')
		
		first_semester.classes.add(edClass)
		first_semester.classes.add(edClass2)
		
		
		bob = Student.objects.create(name="Bob DaBuilder")
		jane = Student.objects.create(name="Jane Doe")

		bobenrollment = Enrollment.objects.create(student=bob, edclass=edClass, grade="Excellent")
		janeenrollment = Enrollment.objects.create(student=jane,edclass=edClass)
		bobenrollment2 = Enrollment.objects.create(student=bob,edclass=edClass2)
		janeenrollment2 = Enrollment.objects.create(student=jane,edclass=edClass2)
		
		
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
		self.add_two_classes_to_semester_add_two_students_to_class()

		saved_classes = EdClasses.objects.all()
		self.assertEqual(saved_classes.count(), 2)

		first_saved_class = saved_classes[0]
		second_saved_class = saved_classes[1]

		self.assertEqual(first_saved_class.name, 'EG 5000')
		self.assertEqual(second_saved_class.name, 'EG 6000')
	
	def test_classes_link_to_semester(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		first_semester = Semester.objects.get(text='201530')
		
		saved_classes = EdClasses.objects.all()
		first_saved_class = saved_classes[0]
		second_saved_class = saved_classes[1]

		self.assertQuerysetEqual(first_semester.classes.filter(name="EG 5000"),[repr(first_saved_class)] )
		self.assertQuerysetEqual(first_semester.classes.filter(name="EG 6000"), [repr(second_saved_class)] )
	
	def test_students_link_to_class(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		
		oneclass = EdClasses.objects.get(name="EG 5000")
		twoclass = EdClasses.objects.get(name="EG 6000")
		
		jane = Student.objects.get(name="Jane Doe")
		bob = Student.objects.get(name="Bob DaBuilder")
		
		self.assertQuerysetEqual(oneclass.students.filter(name="Jane Doe"), [repr(jane)])
		self.assertQuerysetEqual(twoclass.students.filter(name="Bob DaBuilder"), [repr(bob)])
	
	def test_enrollment_model_creates_correct_number_of_enrollments(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		enrollments = Enrollment.objects.all()

		self.assertEqual(enrollments.count(),4)
	
	def test_students_link_to_enrollments(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		edclass1 = EdClasses.objects.get(name="EG 5000")
		bob = Student.objects.get(name="Bob DaBuilder")
		bobenrollment = Enrollment.objects.get(edclass=edclass1, student=bob)
		self.assertEqual(bobenrollment.grade, "Excellent")
	
	def test_grade_model_links_to_enrollments(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		#gradeForClass = Enrollment.objects.get
