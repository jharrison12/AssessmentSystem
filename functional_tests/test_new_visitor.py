from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from rubricapp.models import Semester, EdClasses

class NewVisitorTest(FunctionalTest):

	def create_two_classes_for_unit_tests(self):
		semester = Semester.objects.create(text="201530")
		EdClasses.objects.create(name="EG 5000", semester=semester)
		EdClasses.objects.create(name="EG 6000", semester=semester)
		
	
	def test_user_visits_inital_page(self):

		# Dr. visits the webpage
		self.create_two_classes_for_unit_tests()
		self.browser.get(self.live_server_url)
		# Dr. Makes sure that it is titled correctly
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
		self.assertEqual(dropdown_list.get_attribute('name'), "Class Name")
		classchoice = self.browser.find_elements_by_tag_name('option')
		self.assertIn("EG 5000", [i.text for i in classchoice])

		#Dr. clicks on a "Choose" button and is taken to a new page
		#submitbutton = self.browser.find_element_by_tag_name	

		#Dr. chooses a student name from a drop down list of student names
		
		#A rubric should appear based upon the key assignment 
		#The rubric should allow the student to click on a matrix of rows
		#The dr. clicks on "submit" the student data is submited to a database
