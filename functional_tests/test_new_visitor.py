from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class NewVisitorTest(FunctionalTest):

	
	def test_user_visits_inital_page(self):

		# Dr. visits the webpage
		self.browser.get(self.live_server_url)
		# Dr. Makes sure that it is titled correctly
		self.assertIn('Assessment System', self.browser.title)

		# Dr. is given the option to choose a class
		header_text = self.browser.find_element_by_tag_name('h3').text
		self.assertIn("Choose a Class!", header_text)

		#Dr. Chooses a class from a list of classes
		dropdown_list = self.browser.find_element_by_tag_name('select')
		self.assertEqual(dropdown_list.get_attribute('name'), "Class Name")
		#Dr. clicks on a "Choose" button and is taken to a new page


		#Dr. chooses a student name from a drop down list of student names
		
		#A rubric should appear based upon the key assignment 
		#The rubric should allow the student to click on a matrix of rows
		#The dr. clicks on "submit" the student data is submited to a database
