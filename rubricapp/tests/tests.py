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
		bob = Student.objects.get(lnumber="21743148")
		request.POST['studentnames'] = bob.lnumber

		response = student_page(request, "/EG5000/")

		self.assertEqual(response.status_code, 302)
		
	def test_class_page_redirects_to_student_url(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		request = HttpRequest()
		request.method = 'POST'
		student = Student.objects.get(lnumber="21743148")
		request.POST['studentnames'] = student.lnumber

		response = student_page(request, "/EG5000/")
		
		self.assertEqual(response.status_code, 302)
		
		self.assertEqual(response['location'], '21743148/')	

class StudentandRubricViewTest(TestCase):

	def add_two_classes_to_semester_add_two_students_to_class_add_one_row(self):
		first_semester = Semester.objects.create(text='201530')
		edClass = EdClasses.objects.create(name='EG 5000') 
		edClass2 = EdClasses.objects.create(name='EG 6000')
		writingrubric = Rubric.objects.create(name="writingrubric")
		first_semester.classes.add(edClass)
		first_semester.classes.add(edClass2)
		
		
		bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
		jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")

		bobenrollment = Enrollment.objects.create(student=bob, edclass=edClass)
		janeenrollment = Enrollment.objects.create(student=jane,edclass=edClass)
		bobenrollment2 = Enrollment.objects.create(student=bob,edclass=edClass2)
		janeenrollment2 = Enrollment.objects.create(student=jane,edclass=edClass2)
		
		row1 = Row.objects.create(excellenttext="THE BEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)
	
		
		
		#Many to many relationship must be added after creation of objects
		#because the manyto-many relationship is not a column in the database

		bobenrollment.keyrubric.add(writingrubric)
	
	def test_studentandrubric_view_returns_correct_template(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get("/EG5000/21743148/")
		self.assertTemplateUsed(response, 'rubric.html')
		
	def test_student_and_rubric_view_shows_student_name(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get("/EG5000/21743148/")
		self.assertContains(response, "DaBuilder, Bob")
	
	def test_student_and_rubric_view_has_excellent_grade(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get("/EG5000/21743148/")
		self.assertContains(response, "Excellent")
	
	def test_rubric_shows_a_cell_under_excellent(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get("/EG5000/21743148/")
		self.assertContains(response, "THE BEST!")
	
	def test_rubric_page_can_take_post_request(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		#response = self.client.get("/EG5000/21743148/")
		request = HttpRequest()
		request.method = 'POST'
		request.POST['id_row_choice'] = 1
		
		response = rubric_page(request, "EG5000", "21743148" )
		self.assertEqual(response.status_code, 302)
		#TODO finish this
		
	def test_post_request_does_not_create_new_row(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		request = HttpRequest()
		edClass = EdClasses.objects.get(name='EG 5000') 
		bob = Student.objects.get(lnumber="21743148")
		bobenrollment = Enrollment.objects.get(student=bob, edclass=edClass)
		writingrubric = bobenrollment.keyrubric.get(name="writingrubric")
		
		row = Row.objects.filter(rubric=writingrubric)
		self.assertEqual(row.count(), 1)
		request.method = 'POST'
		request.POST['id_row_choice'] = 2
		response = rubric_page(request, "EG5000", "21743148")
		
		self.assertEqual(row.count(), 1)
	
	def test_post_request_updates_correct_model(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		
		edClass = EdClasses.objects.get(name='EG 5000') 
		bob = Student.objects.get(lnumber="21743148")
		bobenrollment = Enrollment.objects.get(student=bob, edclass=edClass)
		writingrubric = bobenrollment.keyrubric.get(name="writingrubric")
		row = Row.objects.get(rubric=writingrubric)
		
		request = HttpRequest()
		request.method = 'POST'
		request.POST['id_1-row_choice'] = 2
		
		response = rubric_page(request, "EG5000", "21743148")
		
		self.assertEqual(row.row_choice, 2)

		

class TestRubricModel(TestCase):
			
	def create_rubric_and_rows_connect_to_class(self):
		first_semester = Semester.objects.create(text='201530')
		edClass = EdClasses.objects.create(name='EG 5000') 
		first_semester.classes.add(edClass)
		writingrubric = Rubric.objects.create(name="writingrubric")
		
		bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
		jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")
		
		row1 = Row.objects.create(excellenttext="THE BEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)
	
		
		
		#Many to many relationship must be added after creation of objects
		#because the manyto-many relationship is not a column in the database
		bobenrollment = Enrollment.objects.create(student=bob, edclass=edClass)
		bobenrollment.keyrubric.add(writingrubric)
		
	def test_rubric_connected_with_enrollment_class(self):
		self.create_rubric_and_rows_connect_to_class()
		rubrics = Rubric.objects.all()
		self.assertEqual(rubrics.count(), 1)
		
	def test_to_make_sure_enrollment_object_matches_with_rubric(self):
		self.create_rubric_and_rows_connect_to_class()
		bob = Student.objects.get(lnumber="21743148")
		edClass = EdClasses.objects.get(name='EG 5000')
		enrollmentObj = Enrollment.objects.get(student=bob, edclass=edClass)
		#should get the only rubric attached to the object
		writingrubric = enrollmentObj.keyrubric.get()
		self.assertEqual(writingrubric.name, "writingrubric")
	
	def test_rubric_object_only_has_one_row(self):
		self.create_rubric_and_rows_connect_to_class()
		writingrubric = Rubric.objects.get(name="writingrubric")
		rows = Row.objects.filter(rubric=writingrubric)
		self.assertEqual(rows.count(), 1)
	
	def test_rubric_object_connects_with_multiple_rows(self):
		#This test is more for the developer than the application.
		self.create_rubric_and_rows_connect_to_class()
		writingrubric = Rubric.objects.get(name="writingrubric")
		row2 = Row.objects.create(excellenttext="THE BEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)
		rows = Row.objects.filter(rubric=writingrubric)
		self.assertEqual(rows.count(), 2)
	
	def test_query_to_pull_rubric_and_check_text(self):
		#Check that row object can be filtered based upon text
		self.create_rubric_and_rows_connect_to_class()
		writingrubric = Rubric.objects.get(name="writingrubric")
		row2 = Row.objects.create(excellenttext="THE GREATEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)
		rows = Row.objects.get(excellenttext="THE GREATEST!")
		self.assertIn(rows.proficienttext, "THE SECOND BEST!")
		
class ClassAndSemesterModelTest(TestCase):
	
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
		
		jane = Student.objects.get(lnumber="21743149")
		bob = Student.objects.get(lnumber="21743148")
		
		self.assertQuerysetEqual(oneclass.students.filter(lnumber="21743149"), [repr(jane)])
		self.assertQuerysetEqual(twoclass.students.filter(lnumber="21743148"), [repr(bob)])
	
	def test_enrollment_model_creates_correct_number_of_enrollments(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		enrollments = Enrollment.objects.all()

		self.assertEqual(enrollments.count(),4)
	
	def test_students_link_to_enrollments(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		edclass1 = EdClasses.objects.get(name="EG 5000")
		bob = Student.objects.get(lnumber="21743148")
		bobenrollment = Enrollment.objects.get(edclass=edclass1, student=bob)
		self.assertEqual(bobenrollment.grade, "Excellent")
	

		
