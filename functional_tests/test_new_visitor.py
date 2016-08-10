from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from rubricapp.models import Semester, EdClasses, Student, Enrollment, Rubric, Row
from time import sleep

class NewVisitorTest(FunctionalTest):

	def create_two_classes_for_unit_tests(self):
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
		
	def test_user_visits_inital_page(self):

		# Dr. visits the webpage
		self.create_two_classes_for_unit_tests()
		self.browser.get(self.live_server_url)
		# Dr. Makes sure that it is titled correctly
		idusername = self.browser.find_element_by_id('id_username')
		idusername.send_keys('bob') 
		passwordbox = self.browser.find_element_by_id('id_password')
		passwordbox.send_keys('bob')
		submitbutton = self.browser.find_element_by_xpath('/html/body/h3[2]/form/input[2]')
		submitbutton.send_keys(Keys.ENTER)
		self.assertIn('Assessment System', self.browser.title)
		
		# Dr. chooses a semester from a drop down list
		semester_header_text = self.browser.find_element_by_id('semester').text
		self.assertIn("Choose a Semester!", semester_header_text)
		semester_dropdown = self.browser.find_element_by_id('semesterdropdown')
		self.assertEqual(semester_dropdown.get_attribute('name'), "semester")
		semesterchoice = self.browser.find_elements_by_tag_name('option')
		self.assertIn('201530', [i.text for i in semesterchoice])

		#Dr. clicks submit to send a post request to a server
		submitbutton = self.browser.find_element_by_id('semestersubmit')
		self.assertEqual(submitbutton.get_attribute('value'), "Submit")
		submitbutton.send_keys(Keys.ENTER)

		##Future funtional test for choosing a semester
		# Dr. is given the option to choose a class
		header_text = self.browser.find_element_by_id('edclass').text
		self.assertIn("Choose a Class!", header_text)

		#Dr. Chooses a class from a list of classes
		dropdown_list = self.browser.find_element_by_id('classdropdown')
		self.assertEqual(dropdown_list.get_attribute('name'), "edClass")
		classchoice = self.browser.find_elements_by_tag_name('option')
		self.assertIn("EG 5000", [i.text for i in classchoice])

		#Dr. clicks on a "Choose" button and is taken to a new page
		submitbutton = self.browser.find_element_by_id('classubmit')
		submitbutton.send_keys(Keys.ENTER)
		chooseAStudent = self.browser.find_element_by_id('choosename')


		#Dr. chooses a student name from a drop down list of student names
		studentnamedropdown = self.browser.find_element_by_id('studentdropdown')
		self.assertEqual(studentnamedropdown.get_attribute('name'), 'studentnames')
		studentname = self.browser.find_elements_by_tag_name('option')
		self.assertIn("Bob DaBuilder", [i.text for i in studentname])
		self.assertIn("Jane Doe", [i.text for i in studentname])
		submitbuttonstudent = self.browser.find_element_by_id('studentsubmit')
		submitbuttonstudent.send_keys(Keys.ENTER) 
		
		#A new page should appear with the students name 

		studentnameheader = self.browser.find_element_by_id('studentheader')
		self.assertIn("DaBuilder, Bob",studentnameheader.text )
			
		#A rubric should appear based upon the key assignment 
		rubricheader = self.browser.find_element_by_id('rubricheader')
		self.assertIn("Writing Rubric", rubricheader.text)
		#The rubric should allow the professor to click on a matrix of rows
		
		row1dropdown = self.browser.find_element_by_id('id_form-0-row_choice')
		row2dropdown = self.browser.find_element_by_id('id_form-1-row_choice')
		self.assertEqual(row1dropdown.get_attribute('name'), 'form-0-row_choice')
		self.assertEqual(row2dropdown.get_attribute('name'), 'form-1-row_choice')
		
		rubricoptions = self.browser.find_elements_by_tag_name('option')
		
		self.assertIn("Excellent", [option.text for option in rubricoptions])
		excellent = self.browser.find_element_by_xpath('//*[@id="id_form-0-row_choice"]/option[2]')
		excellent.click()
		sleep(2)

		#The dr. clicks on "submit" the student data is submited to a database
		submitbutton = self.browser.find_element_by_id('rubricsubmit')
		submitbutton.send_keys(Keys.ENTER)
		
		#Clicking submit should save rubric and return to the main student page
		studentnamedropdown = self.browser.find_element_by_id('studentdropdown')
		self.assertEqual(studentnamedropdown.get_attribute('name'), 'studentnames')
		
		#Dr. chooses a different name and fills out a COMPLETELY new rubric 
		studentnames = self.browser.find_elements_by_tag_name('option')
		janedoe = self.browser.find_element_by_id('21743149')
		janedoe.click()
		submitbuttonstudent = self.browser.find_element_by_id('studentsubmit')
		submitbuttonstudent.send_keys(Keys.ENTER) 
		excellent = self.browser.find_element_by_xpath('//*[@id="id_form-0-row_choice"]/option[2]')
		
		#First choice should not be excellent it should be null
		self.assertNotEqual(excellent.get_attribute("selected"), "true")
		excellent = self.browser.find_element_by_xpath('//*[@id="id_form-0-row_choice"]/option[2]')
		excellent.click()
		submitbuttonstudent = self.browser.find_element_by_id('rubricsubmit')
		submitbuttonstudent.send_keys(Keys.ENTER) 
		
		#The new webpage should say "No more students"
		bodytext = self.browser.find_element_by_tag_name('body')
		self.assertIn("There are no more students",bodytext.text)
		
		#The mischevious professor tries to go back to a completed student url
		
		self.browser.get("%s%s" % (self.live_server_url, '/201530/EG5000/21743148'))
		bodytext = self.browser.find_element_by_tag_name('body')
		sleep(25)
		self.assertIn("You have already created a rubric for this student.", bodytext.text)
		
		
