from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from rubricapp.models import Semester, EdClasses, Student, Enrollment, Rubric, Row
from time import sleep
from django.contrib.auth.models import User

class DataView(FunctionalTest):
	
	def create_two_classes_for_unit_tests(self):
		semester = Semester.objects.create(text="201530")
		semester2 = Semester.objects.create(text="201610")
		edclass1 = EdClasses.objects.create(name="EG 5000", teacher=self.test_user, crn=2222)
		edclass2 = EdClasses.objects.create(name="EG 6000", teacher=self.test_user, crn=3333)
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

		row1 = Row.objects.create(name="Excellence",
								  excellenttext="THE BEST!", 
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
		row1 = Row.objects.create(name="Excellence",
								  excellenttext="THE BEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=completedrubricforbob, row_choice=1)
								  
		row2 = Row.objects.create(excellenttext="THE GREATEST!",
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=completedrubricforbob, row_choice=1)
								  
		bobenrollment.completedrubric = completedrubricforbob
		bobenrollment.rubriccompleted = True
		
		bobenrollment.save()
	
	def test_professor_visits_the_main_page(self):
		#Professor pulls up the data view
		self.create_two_classes_for_unit_tests()
		self.browser.get("%s%s" % (self.live_server_url, '/data/'))
		# Prof must first login to the assessment system
		idusername = self.browser.find_element_by_id('id_username')
		idusername.send_keys('bob') 
		passwordbox = self.browser.find_element_by_id('id_password')
		passwordbox.send_keys('bob')
		submitbutton = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/h3[2]/form/input[2]')
		submitbutton.send_keys(Keys.ENTER)
		##TODO logging takes user back to assessmentpage
		self.browser.get("%s%s" % (self.live_server_url, '/data/'))
		#Prof finds several options for how to view rubrics
		headertext = self.browser.find_element_by_id('headertext')
		self.assertEquals(headertext.text, "Choose a data retrieval method")
		studentchoice = self.browser.find_element_by_id('studentlink')
		self.assertEquals(studentchoice.text, "Look at one student's rubrics")
		classchoice = self.browser.find_element_by_id('classlink')
		self.assertEquals(classchoice.text, "Look at aggregated class data")
		
		#Professor Chooses the student view
		studentchoice.click()
		studentchoiceheader = self.browser.find_element_by_id("studentchoice")
		self.assertEqual(studentchoiceheader.text, "Choose a student!")
		
		#Professor Encounters a magical drop down menu with student names
		studentdropdown = self.browser.find_element_by_id('studentnames')
		self.assertEqual(studentdropdown.get_attribute('name'), 'studentnames')
		studentname = self.browser.find_elements_by_tag_name('option')
		self.assertIn("Bob DaBuilder", [i.text for i in studentname])
		submitbuttonstudent = self.browser.find_element_by_id('studentsubmit')
		submitbuttonstudent.send_keys(Keys.ENTER) 
		
		#Professor chooses a rubric
		studentnameheader = self.browser.find_element_by_tag_name('h3')
		self.assertIn("Bob DaBuilder", studentnameheader.text)
		rubricnames = self.browser.find_elements_by_tag_name('option')
		self.assertIn("EG500021743148201530", [i.text for i in rubricnames])
		submitbuttonstudent = self.browser.find_element_by_id('rubricsubmit')
		submitbuttonstudent.send_keys(Keys.ENTER)
		
		#Professor sees the rubric
		bodytext = self.browser.find_element_by_tag_name('body')
		self.assertIn("Excellence", bodytext.text)

		#Prof changes their minds.  They want to look at all the rubrics from a particular course
		self.browser.get("%s%s" % (self.live_server_url, '/data/'))
		classchoice = self.browser.find_element_by_id('classlink')
		classchoice.click()
		
		#Prof must choose by a semester.  OH MY
		semesterdropdown = self.browser.find_element_by_id('semesterselectid')
		semesternames = self.browser.find_elements_by_tag_name('option')
		self.assertIn('201530', [i.text for i in semesternames])
		submitbutton = self.browser.find_element_by_id('semestersubmit')
		submitbutton.send_keys(Keys.ENTER)
		
		#Prof sees that there is a class there
		classdropdown = self.browser.find_element_by_id('edlcassdropdown')
		self.assertEqual(classdropdown.get_attribute('name'), 'edclass')
		classnames = self.browser.find_elements_by_tag_name('option')
		self.assertIn("EG 5000", [i.text for i in classnames])
		submitbutton = self.browser.find_element_by_id('classsubmit')
		submitbutton.send_keys(Keys.ENTER)
		
		#The following page should show the aggregate rubric data for the WHOLE class YAY!
		bodytext = self.browser.find_element_by_tag_name('body')
		self.assertIn("Excellence", bodytext.text)
		self.assertIn("1", bodytext.text)
		
		#Professor Decides to go back to the home page
		self.assertIn("Return to data home", bodytext.text)
		self.browser.find_element_by_link_text('Return to data home').click()
		
		#Prof 
		
		