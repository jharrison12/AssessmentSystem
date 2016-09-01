from unittest import skip
from rubricapp.models import Semester, EdClasses, Student, Enrollment, Rubric, Row
from django.template.loader import render_to_string
from django.http import HttpRequest
from django.test import TestCase, Client
from rubricapp.views import home_page, semester_page, student_page, rubric_page
from django.core.urlresolvers import resolve
from bs4 import BeautifulSoup
from django.contrib.auth.models import UserManager, User

class HomePageTest(TestCase):
	maxDiff = None

	def create_two_semesters_for_unit_tests(self):
		Semester.objects.create(text="201530")
		Semester.objects.create(text="201610")
		self.client = Client()
		self.username = 'bob'
		self.email = 'test@test.com'
		self.password = 'test'
		self.test_user = User.objects.create_user(self.username, self.email, self.password)
		login = self.client.login(username=self.username, password = self.password)
	
	def test_home_url_resolves_to_home_page_view(self):
		found = resolve('/assessment/')
		self.assertEqual(found.func, home_page) 
	
	def test_home_page_returns_correct_html(self):
		self.create_two_semesters_for_unit_tests()
		request = HttpRequest()
		Bob = User.objects.get(username='bob')
		request.user = Bob
		response = home_page(request)
		semesters = Semester.objects.all()
		expected_html = render_to_string('rubricapp/home.html', { 'semestercode': semesters })
		self.assertMultiLineEqual(response.content.decode(), expected_html)

	def test_home_page_can_redirects_after_Post_request(self):
		self.create_two_semesters_for_unit_tests()
		request = HttpRequest()
		Bob = User.objects.get(username='bob')
		request.user = Bob
		request.method = 'POST'
		semester = Semester.objects.get(text="201530")
		request.POST['semester'] = semester.text

		response = home_page(request)
		
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '201530/')
		
	def test_home_page_shows_two_semesters(self):
		self.create_two_semesters_for_unit_tests()
		request = HttpRequest()
		Bob = User.objects.get(username='bob')
		request.user = Bob
		response = home_page(request)
		self.assertEqual(Semester.objects.count(), 2)

	def test_home_page_template_has_two_semesters(self):
		self.create_two_semesters_for_unit_tests()
		request = HttpRequest()
		Bob = User.objects.get(username='bob')
		request.user = Bob
		response = home_page(request)
		self.assertIn('201530', response.content.decode())
		self.assertIn('201610', response.content.decode())

class SemesterClassViewTest(TestCase):
	
	def setUp(self):
		self.client = Client()
		self.username = 'bob'
		self.email = 'test@test.com'
		self.password = 'bob'        
		self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
		login = self.client.login(username=self.username, password=self.password)
		self.assertEqual(login, True)
		
	def test_bob_cannot_see_jane_class(self):
		semester = Semester.objects.create(text="201530")
		jane = User.objects.create(username="Jane")
		edclass1 = EdClasses.objects.create(name="EG 5111", teacher=jane)
		semester.classes.add(edclass1)
		response = self.client.get('/assessment/201530/')
		self.assertNotIn("EG 5111", response.content.decode())
	
	def test_bob_can_see_bob_class(self):
		semester = Semester.objects.create(text="201530")
		jane = User.objects.create(username="Jane")
		edclass1 = EdClasses.objects.create(name="EG 5111", teacher=self.test_user)
		semester.classes.add(edclass1)
		response = self.client.get('/assessment/201530/')
		self.assertIn("EG 5111", response.content.decode())
	
	def test_displays_all_classes(self):
		semester = Semester.objects.create(text="201530")
		edclass1 = EdClasses.objects.create(name="EG 5000", teacher=self.test_user)
		semester.classes.add(edclass1)
		
		response = self.client.get('/assessment/'+semester.text+'/')
		self.assertContains(response, 'EG 5000') 
	
	def create_two_classes_for_unit_tests(self):
		semester = Semester.objects.get(text="201530")
		class1 = EdClasses.objects.create(name="EG 5000", teacher=self.test_user)
		class2 = EdClasses.objects.create(name="EG 6000", teacher=self.test_user)
		semester.classes.add(class1)
		semester.classes.add(class2)
		
	def create_two_semesters_for_unit_tests(self):
		Semester.objects.create(text="201530")
		Semester.objects.create(text="201610")
		
	def test_displays_two_classes(self):
		self.create_two_semesters_for_unit_tests()
		self.create_two_classes_for_unit_tests()
		semester = Semester.objects.get(text="201530")
		response = self.client.get('/assessment/'+ semester.text +'/')
		self.assertContains(response, "EG 6000")
		self.assertContains(response, "EG 5000")
		
	def test_semester_view_returns_correct_templates(self):
		self.create_two_semesters_for_unit_tests()
		self.create_two_classes_for_unit_tests()
		semester = Semester.objects.get(text="201530")
		response = self.client.get('/assessment/'+ semester.text +'/')
		self.assertTemplateUsed(response, 'rubricapp/semester.html')
		
	def test_home_page_can_visit_201610_in_url(self):
		self.create_two_semesters_for_unit_tests()
		request = HttpRequest()
		Bob = User.objects.get(username='bob')
		request.user = Bob
		request.method = 'POST'
		semester = Semester.objects.get(text="201610")
		request.POST['semester'] = semester.text

		response = home_page(request)
		
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '201610/')	
	
	def test_semester_page_can_take_post_request(self):
		self.create_two_semesters_for_unit_tests()
		self.create_two_classes_for_unit_tests()
		request = HttpRequest()
		bob = User.objects.get(username="bob")
		request.user = bob
		request.method = "POST"
		edClass = EdClasses.objects.get(name="EG 5000", teacher=self.test_user)
		request.POST['edClass'] = edClass.name

		response = semester_page(request, "201530")

		self.assertEqual(response.status_code, 302)

class ClassViewTest(TestCase):

	def add_two_classes_to_semester_add_two_students_to_class(self):
		self.client = Client()
		self.username = 'bob'
		self.email = 'test@test.com'
		self.password = 'test'
		self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
		login = self.client.login(username=self.username, password = self.password)
		jane = User.objects.create(username="Jane")
		
		
		first_semester = Semester.objects.create(text='201530')
		edClass = EdClasses.objects.create(name='EG 5000', teacher=self.test_user) 
		edClass2 = EdClasses.objects.create(name='EG 6000', teacher=self.test_user)
		edClass1 = EdClasses.objects.create(name="EG 5111", teacher=jane)
		
		first_semester.classes.add(edClass)
		first_semester.classes.add(edClass2)
		first_semester.classes.add(edClass1)
		
		
		bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
		jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")
		kelly = Student.objects.create(lastname="Smith", firstname="Kelly", lnumber="33333333")
		
		bobenrollment = Enrollment.objects.create(student=bob, edclass=edClass, semester=first_semester)
		janeenrollment = Enrollment.objects.create(student=jane,edclass=edClass, semester=first_semester)
		bobenrollment2 = Enrollment.objects.create(student=bob,edclass=edClass2, semester=first_semester)
		janeenrollment2 = Enrollment.objects.create(student=jane,edclass=edClass2, semester=first_semester)
		kellyenrollment = Enrollment.objects.create(student=kelly, edclass=edClass1, semester=first_semester)
		
		
	def test_user_logs_in(self):
		self.client = Client()
		self.username = 'bob'
		self.email = 'test@test.com'
		self.password = 'test'
		self.test_user = User.objects.create_user(self.username, self.email, self.password)
		login = self.client.login(username=self.username, password = self.password)
		self.assertEqual(login, True)
		
	def test_bob_cannot_see_jane_students(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		response = self.client.get('/assessment/201530/EG5111/')
		self.assertNotIn("Smith", response.content.decode())
		
	def test_jane_class_results_in_404(self):
		#bob is logged in right now.  shouldnt see jane class
		self.add_two_classes_to_semester_add_two_students_to_class()
		response = self.client.get('/assessment/201530/EG5111/')
		self.assertEqual(response.status_code, 404)
		
	
	def test_semester_page_requires_login(self):
		#follow=True follows the redirect to the login page
		response = self.client.get("/assessment/201530/", follow=True)
		self.assertIn("Username", response.content.decode())
	
	def test_student_page_returns_correct_template(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		response = self.client.get("/assessment/201530/EG5000/")
		self.assertTemplateUsed(response, 'rubricapp/student.html')
		
	def test_semester_page_redirects_to_class_url(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		request = HttpRequest()
		Bob = User.objects.get(username='bob')
		request.user = Bob
		request.method = "POST"
		edClass = EdClasses.objects.get(name="EG 5000")
		request.POST['edClass'] = edClass.name

		response = semester_page(request, "201530")
		
		self.assertEqual(response['location'], 'EG5000/')
	
	def test_semester_page_can_show_without_redirecting(self):
		#TODO setup semester/class/ url
		self.add_two_classes_to_semester_add_two_students_to_class()
		response = self.client.get("/assessment/201530/EG5000/")

		self.assertContains(response, 'Bob DaBuilder')
	
	def test_class_page_can_take_post_request(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		request = HttpRequest()
		request.method = "POST"
		Bob = User.objects.get(username='bob')
		request.user = Bob
		bob = Student.objects.get(lnumber="21743148")
		request.POST['studentnames'] = bob.lnumber

		response = student_page(request, "EG5000", "201530")

		self.assertEqual(response.status_code, 302)
		
	def test_class_page_redirects_to_student_url(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		request = HttpRequest()
		request.method = 'POST'
		Bob = User.objects.get(username='bob')
		request.user = Bob
		student = Student.objects.get(lnumber="21743148")
		request.POST['studentnames'] = student.lnumber

		response = student_page(request, "EG5000", "201530")
		
		self.assertEqual(response.status_code, 302)
		
		self.assertEqual(response['location'], '21743148/')	
		
	def test_class_page_shows_url_if_no_students(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		bobenrollment = Enrollment.objects.get(student__lastname="DaBuilder", edclass__name="EG 5000")
		bobenrollment.rubriccompleted = True
		bobenrollment.save()
		janeenrollment = Enrollment.objects.get(student__lastname="Doe", edclass__name="EG 5000")
		janeenrollment.rubriccompleted = True
		janeenrollment.save()
		
		response = self.client.get("/assessment/201530/EG5000/")
		self.assertIn("Return to the semester page", response.content.decode())
		
	def test_class_page_does_not_show_students_from_other_semesters(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		booritter = Student.objects.create(lastname="Ritter", firstname="Elaine", lnumber="21743142")
		newsemester = Semester.objects.create(text="201610")
		edclass = EdClasses.objects.get(name="EG 5000")
		newsemester.classes.add(edclass)
		booenrollment = Enrollment.objects.create(student=booritter, edclass=edclass, semester=newsemester)
		response = self.client.get('/assessment/201530/EG5000/')
		self.assertNotContains(response, "Elaine")
		

class StudentandRubricViewTest(TestCase):

	def add_two_classes_to_semester_add_two_students_to_class_add_one_row(self):
		self.client = Client()
		self.username = 'bob'
		self.email = 'test@test.com'
		self.password = 'test'
		self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
		login = self.client.login(username=self.username, password = self.password)
		jane = User.objects.create(username="Jane")
		
		semester = Semester.objects.create(text="201530")
		edclass1 = EdClasses.objects.create(name="EG 5000", teacher=self.test_user)
		edclass2 = EdClasses.objects.create(name="EG 6000",  teacher=self.test_user)
		edclass = EdClasses.objects.create(name="EG 5111", teacher=jane)
		semester.classes.add(edclass1)
		semester.classes.add(edclass2)
		semester.classes.add(edclass)
		
		bob = Student.objects.create(lastname="DaBuilder", firstname="Bob",lnumber="21743148")
		jane = Student.objects.create(lastname="Doe", firstname="Jane",lnumber="21743149")
		kelly = Student.objects.create(lastname="Smith", firstname="Kelly", lnumber="33333333")
		
		kellyenrollment = Enrollment.objects.create(student=kelly, edclass=edclass, semester=semester)
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
		edclass.keyrubric.add(writingrubric)

		
	def test_rubric_page_not_viewable_by_dasterdaly_bob(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get('/assessment/201530/EG5111/33333333/')
		self.assertEquals(response.status_code, 404)
		
	def test_class_page_requires_login(self):
		response = self.client.get("/assessment/201530/EG5000", follow=True)
		self.assertIn("Username", response.content.decode())

	def test_student_and_rubric_view_returns_correct_template(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get("/assessment/201530/EG5000/21743148/")
		self.assertTemplateUsed(response, 'rubricapp/rubric.html')
		
	def test_student_and_rubric_view_shows_student_name(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get("/assessment/201530/EG5000/21743148/")
		self.assertContains(response, "DaBuilder, Bob")
	
	def test_student_and_rubric_view_has_excellent_grade(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get("/assessment/201530/EG5000/21743148/")
		self.assertContains(response, "Excellent")
	
	def test_rubric_shows_a_cell_under_excellent(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get("/assessment/201530/EG5000/21743148/")
		self.assertContains(response, "THE BEST!")
	#TODO FINISH THE THREE TESTS BELOW
	
	def test_rubric_page_shows_rubric_name(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		response = self.client.get("/assessment/201530/EG5000/21743148/")
		self.assertContains(response, "Writing Rubric")
	
	def test_rubric_page_can_take_post_request(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		
		response = self.client.get("/assessment/201530/EG5000/21743148/")
		#soup = BeautifulSoup(response.content)
		#form = soup.find('form')
		#print(form)
		data ={"form-TOTAL_FORMS": "2",
			   "form-INITIAL_FORMS": "2",
			   "form-MIN_NUM_FORMS": "0",
			   "form-MAX_NUM_FORMS": "1000",
			   "form-0-row_choice":"1", 
			   "form-1-row_choice":"2", 
			   "form-0-id": "3",
			   "form-1-id": "4"}
		response = self.client.post("/assessment/201530/EG5000/21743148/", data)

		self.assertEqual(response.status_code, 302)
	
	def test_post_request_creates_new_rubric_for_the_enrollment(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()

		writingrubric = Rubric.objects.get(name="writingrubric")
		
		row = Row.objects.filter(rubric=writingrubric)
		self.assertEqual(row.count(), 2)
		#Why do you need to get the response before you can post it?????
		response = self.client.get("/assessment/201530/EG5000/21743148/")
		data ={"form-TOTAL_FORMS": "2",
			   "form-INITIAL_FORMS": "2",
			   "form-MIN_NUM_FORMS": "0",
			   "form-MAX_NUM_FORMS": "1000",
			   "form-0-row_choice":"1", 
			   "form-1-row_choice":"2", 
			   "form-0-id": "3",
			   "form-1-id": "4"}
			   
		response = self.client.post("/assessment/201530/EG5000/21743148/", data)
		student = Student.objects.get(lnumber="21743148")
		edclass = EdClasses.objects.get(name="EG 5000")
		
		bobenrollment = Enrollment.objects.get(student=student, edclass=edclass)
		
		self.assertEqual(bobenrollment.completedrubric.name, "EG500021743148201530")
		
	def test_rubric_page_redirects_correct_page(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
		
		response = self.client.get("/assessment/201530/EG5000/21743148/")
		#soup = BeautifulSoup(response.content)
		#form = soup.find('form')
		#print(form)
		data ={"form-TOTAL_FORMS": "2",
			   "form-INITIAL_FORMS": "2",
			   "form-MIN_NUM_FORMS": "0",
			   "form-MAX_NUM_FORMS": "1000",
			   "form-0-row_choice":"1", 
			   "form-1-row_choice":"2", 
			   "form-0-id": "3",
			   "form-1-id": "4"}
		response = self.client.post("/assessment/201530/EG5000/21743148/", data)

		self.assertEqual(response['location'], 'http://testserver/assessment/201530/EG5000/')	
		
	
	def test_post_request_updates_correct_model(self):
		self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()

		#Why do you need to get the response before you can post it?????
		response = self.client.get("/assessment/201530/EG5000/21743148/")
		data ={"form-TOTAL_FORMS": "2",
			   "form-INITIAL_FORMS": "2",
			   "form-MIN_NUM_FORMS": "0",
			   "form-MAX_NUM_FORMS": "1000",
			   "form-0-row_choice":"1", 
			   "form-1-row_choice":"2", 
			   "form-0-id": "3",
			   "form-1-id": "4"}
			   
		response = self.client.post("/assessment/201530/EG5000/21743148/", data)
		student = Student.objects.get(lnumber="21743148")
		edclass = EdClasses.objects.get(name="EG 5000")
		
		bobenrollment = Enrollment.objects.get(student=student, edclass=edclass)
		row = Row.objects.get(excellenttext="THE BEST!", rubric__name=bobenrollment.completedrubric.name)
		self.assertEqual(row.row_choice, "1")
		

		
class UserLoginTest(TestCase):

	def test_login_page_exists(self):
		response  = self.client.get('/assessment/201530/')
		self.assertEqual(response.status_code, 302)
	
	def test_login_page_takes_name(self):
		response = self.client.get('/login/')
		self.assertTemplateUsed(response, 'registration/login.html')
		
