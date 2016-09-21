from django.test import TestCase, Client
from unittest import skip
from django.core.urlresolvers import resolve
from dataview.views import home_page, student_view, student_data_view, ed_class_view, ed_class_data_view, semester_ed_class_view
from rubricapp.models import Semester, Student, Enrollment, EdClasses, Rubric, Row
from django.contrib.auth.models import User
from django.http import HttpRequest
import re
from django.contrib.auth.models import User

# Create your tests here.

class DataViewHome(TestCase):

	def setUp(self):
		Semester.objects.create(text="201530")
		Semester.objects.create(text="201610")
		self.client = Client()
		self.username = 'bob'
		self.email = 'test@test.com'
		self.password = 'test'
		self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
		login = self.client.login(username=self.username, password = self.password)

	def test_data_view_home_returns_function(self):
		found = resolve('/data/')
		self.assertEqual(found.func, home_page)
		
	def test_data_view_home(self):
		response = self.client.get('/data/')
		self.assertContains(response, 'You', status_code=200)
		
	def test_data_view_home_uses_template(self):
		response = self.client.get('/data/')
		self.assertTemplateUsed(response, 'dataview/dataviewhome.html')
		
	def test_data_view_home_only_viewable_by_user(self):
		self.client.logout()
		response = self.client.get('/data/')
		self.assertRedirects(response, '/login/?next=/data/',status_code=302)
		
	def test_data_view_home_only_viewable_to_superuser(self):
		self.client.logout()
		kathy = User.objects.create_user(username="kathy", password="b")
		istrue = self.client.login(username="kathy", password="b")
		self.assertEquals(istrue, True)
		response = self.client.get('/data/')
		self.assertRedirects(response, '/login/?next=/data/', status_code=302)
		
		
class StudentView(TestCase):

	def setUp(self):
		semester = Semester.objects.create(text="201530")
		semester2 = Semester.objects.create(text="201610")
		jacob = User.objects.create(username="jacob")
		edclass1 = EdClasses.objects.create(name="EG 5000",teacher=jacob, crn=2222)
		edclass2 = EdClasses.objects.create(name="EG 6000",teacher=jacob, crn=3333)
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
		
		completedrubricforbob = Rubric.objects.create(name="EG500021743148201530", template=False)
		row1 = Row.objects.create(name="Fortitude",
								  excellenttext="THE BEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=completedrubricforbob, row_choice=2)
								  
		row2 = Row.objects.create(name="Excellenceisahabit",
								  excellenttext="THE GREATEST!",
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=completedrubricforbob, row_choice=1)
		
		bobenrollment.completedrubric = completedrubricforbob
		bobenrollment.rubriccompleted = True
		bobenrollment.save()
		self.client = Client()
		self.username = 'bob'
		self.email = 'test@test.com'
		self.password = 'test'
		self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
		login = self.client.login(username=self.username, password = self.password)
		
		
	def test_student_view_uses_student_view_function(self):
		found = resolve('/data/student/')
		self.assertEqual(found.func, student_view)
	
	def test_student_view_works(self):
		response = self.client.get('/data/student/')
		self.assertContains(response, "Choose a student!")
	
	def test_student_view_requires_login(self):
		self.client.logout()
		response = self.client.get('/data/student/')
		self.assertRedirects(response, '/login/?next=/data/student/', status_code=302)
	
	def test_student_view_requires_superuser(self):
		self.client.logout()
		kathy = User.objects.create_user(username="kathy", password="b")
		istrue = self.client.login(username="kathy", password="b")
		self.assertEquals(istrue, True)
		response = self.client.get('/data/student/')
		self.assertRedirects(response, '/login/?next=/data/student/', status_code=302)
	
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
		request.user = self.test_user
		request.POST['studentnames'] = "Bob Dabuilder"
		response = student_view(request)
		self.assertEqual(response.status_code, 302)
		
	def test_student_page_redirects_to_individual_student_page(self):
		request = HttpRequest()
		request.method = "POST"
		request.user = self.test_user
		request.POST['studentnames'] = "21743148"
		response = student_view(request)
		self.assertEqual(response['location'], '21743148/')
		
	def test_bob_student_data_view_page_requires_login(self):
		self.client.logout()
		response = self.client.get('/data/student/21743148/')
		self.assertRedirects(response, '/login/?next=/data/student/21743148/', status_code=302)
	
	def test_student_data_view_requires_superuser(self):
		self.client.logout()
		kathy = User.objects.create_user(username="kathy",password="b")
		istrue = self.client.login(username="kathy", password="b")
		self.assertEquals(istrue, True)
		response = self.client.get('/data/student/21743148/')
		self.assertRedirects(response, '/login/?next=/data/student/21743148/', status_code=302)
	
	def test_dataview_page_exists_for_bob(self):
		response = self.client.get('/data/student/21743148/')
		self.assertIn("Bob", response.content.decode())
		
	def test_data_view_shows_rubrics(self):
		response = self.client.get('/data/student/21743148/')
		self.assertIn("EG500021743148201530", response.content.decode())
		
	def test_student_data_page_has_submit_button(self):
		response = self.client.get("/data/student/21743148/")
		self.assertIn("Submit", response.content.decode())
		
	def test_student_data_view_takes_post_request(self):
		request = HttpRequest()
		request.method = "POST"
		request.POST['rubricname'] ="bobcompletedrubric"
		request.user = self.test_user
		response = student_data_view(request,lnumber="21743148")
		self.assertEqual(response.status_code, 302)
	
	def test_student_data_view_redirects_to_correct_url(self):
		request = HttpRequest()
		request.method = "POST"
		request.POST['rubricname'] = "EG5000 21743148 201530"
		request.user = self.test_user
		response = student_data_view(request, lnumber="21743148")
		self.assertEqual(response['location'], 'EG500021743148201530/')
	
	def test_student_rubric_view_shows_a_rubric(self):
		response = self.client.get('/data/student/21743148/EG500021743148201530/')
		self.assertIn("Rubric", response.content.decode())
	
	def test_student_rubric_view_uses_correct_template(self):
		response = self.client.get('/data/student/21743148/EG500021743148201530/')
		self.assertTemplateUsed(response, 'dataview/studentrubricview.html')
		
	def test_student_rubric_view_shows__rows(self):
		response = self.client.get('/data/student/21743148/EG500021743148201530/')
		self.assertIn("Excellenceisahabit", response.content.decode())
	
	def test_student_rubric_view_shows_scores(self):
		response = self.client.get('/data/student/21743148/EG500021743148201530/')
		self.assertIn("The worst ever", response.content.decode())
		
	def test_student_rubic_view_requires_login(self):
		self.client.logout()
		response = self.client.get('/data/student/21743148/EG500021743148201530/')
		self.assertRedirects(response, '/login/?next=/data/student/21743148/EG500021743148201530/', status_code=302)
	
	def test_student_rubric_view_requires_superuser(self):
		self.client.logout()
		kathy = User.objects.create_user(username="kathy", password="b")
		istrue = self.client.login(username="kathy", password="b")
		self.assertEquals(istrue, True)
		response = self.client.get("/data/student/21743148/EG500021743148201530/")
		self.assertRedirects(response, '/login/?next=/data/student/21743148/EG500021743148201530/', status_code=302)
		
class EdClass(TestCase):
	
	def setUp(self):
		semester = Semester.objects.create(text="201530")
		semester2 = Semester.objects.create(text="201610")
		kelly = User.objects.create(username="kelly")
		edclass1 = EdClasses.objects.create(name="EG 5000", teacher=kelly, crn=2222)
		edclass2 = EdClasses.objects.create(name="EG 6000", teacher=kelly, crn=3333)
		semester.classes.add(edclass1)
		semester.classes.add(edclass2)
		
		bob = Student.objects.create(lastname="DaBuilder", firstname="Bob",lnumber="21743148")
		jane = Student.objects.create(lastname="Doe", firstname="Jane",lnumber="21743149")
		jake = Student.objects.create(lastname="The Snake", firstname="Jake", lnumber="0000")
		
		bobenrollment = Enrollment.objects.create(student=bob, edclass=edclass1, semester=semester)
		bobenrollment1 = Enrollment.objects.create(student=bob, edclass=edclass2, semester=semester)
		janeenrollment = Enrollment.objects.create(student=jane, edclass=edclass1, semester=semester)
		janeenrollment2 = Enrollment.objects.create(student=jane, edclass=edclass2, semester=semester)
		jakeenrollment = Enrollment.objects.create(student=jake, edclass=edclass1, semester=semester2)
		writingrubric = Rubric.objects.create(name="writingrubric")

		row1 = Row.objects.create(name="Fortitude",
								  excellenttext="THE BEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)
								  
		row2 = Row.objects.create(name="Excellenceisahabit",
								  excellenttext="THE GREATEST!",
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)
		
		#Many to many relationship must be added after creation of objects
		#because the manyto-many relationship is not a column in the database
		edclass1.keyrubric.add(writingrubric)
		edclass2.keyrubric.add(writingrubric)
		
		completedrubricforbob = Rubric.objects.create(name="EG500021743148201530", template=False)
		row1 = Row.objects.create(name="Fortitude",
								  excellenttext="THE BEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=completedrubricforbob, row_choice=2)
								  
		row2 = Row.objects.create(name="Excellenceisahabit",
								  excellenttext="THE GREATEST!",
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=completedrubricforbob, row_choice=4)
		
		bobenrollment.completedrubric = completedrubricforbob
		bobenrollment.rubriccompleted = True
		bobenrollment.save()	
		
		completedrubricforbobeg6000 = Rubric.objects.create(name="EG600021743148201530", template=False)
		row1 = Row.objects.create(name="Fortitude",
								  excellenttext="THE BEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=completedrubricforbobeg6000, row_choice=1)
								  
		row2 = Row.objects.create(name="Excellenceisahabit",
								  excellenttext="THE GREATEST!",
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=completedrubricforbobeg6000, row_choice=1)
		bobenrollment1.completedrubric = completedrubricforbobeg6000
		bobenrollment1.save()
								  
		completedrubricforjane = Rubric.objects.create(name="EG500021743149201530", template=False)
		row1 = Row.objects.create(name="Fortitude",
								  excellenttext="THE BEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=completedrubricforjane, row_choice=1)
								  
		row2 = Row.objects.create(name="Excellenceisahabit",
								  excellenttext="THE GREATEST!",
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=completedrubricforjane, row_choice=1)
		
		janeenrollment.completedrubric = completedrubricforjane
		janeenrollment.rubriccompleted = True
		janeenrollment.save()	
		
		completedrubricforjake = Rubric.objects.create(name="EG50000000201610", template=False)
		row1 = Row.objects.create(name="Fortitude",
								  excellenttext="THE BEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=completedrubricforjake, row_choice=4)
		row2 = Row.objects.create(name="Excellenceisahabit",
								  excellenttext="THE GREATEST!",
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=completedrubricforjake, row_choice=4)
		
		jakeenrollment.completedrubric = completedrubricforjake
		jakeenrollment.rubriccompleted = True
		jakeenrollment.save()
		self.client = Client()
		self.username = 'bob'
		self.email = 'test@test.com'
		self.password = 'test'
		self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
		login = self.client.login(username=self.username, password = self.password)
		
	def test_class_view_requires_login(self):
		self.client.logout()
		response = self.client.get('/data/class/')
		self.assertRedirects(response, '/login/?next=/data/class/', status_code=302)
		
	def test_class_view_requires_superuser_login(self):
		self.client.logout()
		kathy = User.objects.create_user(username="kathy", password="b")
		istrue = self.client.login(username="kathy", password="b")
		self.assertEquals(istrue, True)
		response = self.client.get('/data/class/')
		self.assertRedirects(response, '/login/?next=/data/class/', status_code=302)
	
	def test_class_view_uses_class_view_function(self):
		found = resolve('/data/class/')
		self.assertEqual(found.func, semester_ed_class_view)
	
	def test_class_view_works(self):
		response = self.client.get('/data/class/')
		self.assertContains(response, "Choose a semester!")
		
	def test_class_view_uses_correct_template(self):
		response = self.client.get('/data/class/')
		self.assertTemplateUsed(response, 'dataview/semesterclassview.html')
		
	def test_semester_class_view_has_semester(self):
		response = self.client.get('/data/class/')
		self.assertContains(response, "201530")
		
	def test_semester_class_view_has_submit_button(self):
		response = self.client.get('/data/class/201530/')
		self.assertContains(response, "Submit")
		
	def test_semester_class_view_requires_login(self):
		self.client.logout()
		response = self.client.get('/data/class/201530/')
		self.assertRedirects(response, '/login/?next=/data/class/201530/', status_code=302)
		
	def test_semester_class_view_requires_superuser_login(self):
		self.client.logout()
		kathy = User.objects.create_user(username="kathy", password="b")
		istrue = self.client.login(username="kathy", password="b")
		self.assertEquals(istrue, True)
		response = self.client.get('/data/class/201530/')
		self.assertRedirects(response, '/login/?next=/data/class/201530/', status_code=302)
	
	def test_semester_class_view_takes_post_request(self):
		request = HttpRequest()
		request.method = "POST"
		request.POST['semesterselect'] = "201530"
		request.user = self.test_user
		response = semester_ed_class_view(request)
		self.assertEqual(response.status_code, 302)
	
	def test_semester_class_view_redirects_to_proper_page(self):
		request = HttpRequest()
		request.method = "POST"
		request.POST['semesterselect'] = "201530"
		request.user = self.test_user
		response = semester_ed_class_view(request)
		self.assertEqual(response['location'], "201530/")
		
	def test_class_page_shows_an_actual_class(self):
		#follow=True follows the redirect to the login page
		response = self.client.get("/data/class/201530/")
		self.assertIn("EG 5000", response.content.decode())
	
	def test_class_page_has_submit_button(self):
		response = self.client.get('/data/class/201530/')
		self.assertIn("Submit", response.content.decode())
	
	def test_class_page_can_take_post_request(self):
		request = HttpRequest()
		request.method = "POST"
		request.POST['edclass'] = "EG 5000"
		request.user = self.test_user
		response = ed_class_view(request, "201530")
		self.assertEqual(response.status_code, 302)
		
	def test_class_page_redirects_to_proper_url(self):
		request = HttpRequest()
		request.method = "POST"
		request.user = self.test_user
		request.POST['edclass'] = "EG 5000"
		response = ed_class_view(request, "201530")
		self.assertEqual(response['location'],"EG5000/" )
		
	def test_class_data_page_returns_correct_function(self):
		found = resolve('/data/class/201530/EG5000/')
		self.assertEqual(found.func, ed_class_data_view)
	
	def test_class_data_page_uses_correct_template(self):
		edclass = EdClasses.objects.get(name="EG 5000")
		edclass = re.sub('[\s+]', '', edclass.name)
		response = self.client.get("/data/class/201530/%s/" % (edclass))
		self.assertTemplateUsed(response, 'dataview/classdataview.html')
		
	def test_class_data_page_requires_login(self):
		self.client.logout()
		response = self.client.get('/data/class/201530/EG5000/')
		self.assertRedirects(response, '/login/?next=/data/class/201530/EG5000/', status_code=302)
		
	def test_semester_class_data_view_requires_superuser_login(self):
		self.client.logout()
		kathy = User.objects.create_user(username="kathy", password="b")
		istrue = self.client.login(username="kathy", password="b")
		self.assertEquals(istrue, True)
		response = self.client.get('/data/class/201530/EG5000/')
		self.assertRedirects(response, '/login/?next=/data/class/201530/EG5000/', status_code=302)
	
	def test_class_rubric_view_shows_rubric(self):
		response = self.client.get('/data/class/201530/EG5000/')
		self.assertIn("Excellenceisahabit", response.content.decode())
	
	def test_class_data_page_shows_aggregated_score(self):
		response = self.client.get('/data/class/201530/EG5000/')
		self.assertIn("1.5", response.content.decode())
	
	def test_EG5000_201530_rubric_data_does_not_appear_in_wrong_semester(self):
		response = self.client.get('/data/class/201610/EG5000/')
		self.assertNotIn("1.5", response.content.decode())
		self.assertNotIn("2.5", response.content.decode())
	
	def test_EG5000_201610_rubric_shows_only_jake_score(self):
		response = self.client.get('/data/class/201610/EG5000/')
		#should only show score of 4.0
		self.assertIn("4.0", response.content.decode())
	
	def test_EG6000_201530_rubric_shows_only_one_score(self):
		response = self.client.get('/data/class/201530/EG6000/')
		self.assertIn("1.0", response.content.decode())

		
