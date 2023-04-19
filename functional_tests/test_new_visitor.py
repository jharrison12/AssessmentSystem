from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from rubricapp.models import Semester, EdClasses, Student, Enrollment, Rubric, Row, Assignment
from time import sleep
from django.contrib.auth.models import User
import sys


class NewVisitorTest(FunctionalTest):
    def create_two_classes_for_unit_tests(self):
        semester = Semester.objects.create(text="201530")
        semester2 = Semester.objects.create(text="201610")
        edclass1 = EdClasses.objects.create(subject="EG", coursenumber="5000", sectionnumber="01",
                                            teacher=self.test_user, crn=2222, semester=semester)
        edclass2 = EdClasses.objects.create(subject="EG", coursenumber="6000", sectionnumber="01",
                                            teacher=self.test_user, crn=3333, semester=semester)
        edclass3 = EdClasses.objects.create(subject="ED", coursenumber="2000", sectionnumber="01",
                                            teacher=self.test_user, crn=4444, semester=semester)
        # semester.classes.add(edclass1)
        # semester.classes.add(edclass2)


        bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
        jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")
        jake = Student.objects.create(lastname="The Snake", firstname="Jake", lnumber="0000")

        bobenrollment = Enrollment.objects.create(student=bob, edclass=edclass1)
        bobenrollment1 = Enrollment.objects.create(student=bob, edclass=edclass2)
        janeenrollment = Enrollment.objects.create(student=jane, edclass=edclass1)
        janeenrollment2 = Enrollment.objects.create(student=jane, edclass=edclass2)
        jakeenrollment = Enrollment.objects.create(student=jake, edclass=edclass3)
        writingrubric = Rubric.objects.create(name="writingrubric")
        unitrubric = Rubric.objects.create(name="unitrubric")

        row1 = Row.objects.create(excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=writingrubric, name="Excellence is a habit")

        row2 = Row.objects.create(excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=writingrubric, name="Mediocrity is a habit")

        row3 = Row.objects.create(excellenttext="AMAZING!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=unitrubric)

        # Many to many relationship must be added after creation of objects
        # because the manyto-many relationship is not a column in the database
        #edclasssemester1.keyrubric.add(writingrubric)
        #edclasssemester1assignment2.keyrubric.add(unitrubric)
        #edclasssemester2.keyrubric.add(writingrubric)

        edclasssemester1 = Assignment.objects.create(edclass=edclass1,
                                                     assignmentname="Writing Assignment", keyrubric=writingrubric)
        edclasssemester1assignment2 = Assignment.objects.create(edclass=edclass1,
                                                                assignmentname="Unit Assignment", keyrubric=unitrubric)
        edclasssemester2 = Assignment.objects.create(edclass=edclass2, keyrubric=writingrubric)

        edclasssemester2 = Assignment.objects.create(edclass=edclass3, keyrubric=writingrubric)

    def test_user_visits_inital_page(self):
        # Dr. visits the webpage
        self.create_two_classes_for_unit_tests()
        self.browser.get(self.server_url + '/assessment/')
        # Dr. must first login to the assessment system
        idusername = self.browser.find_element_by_id('id_username')
        idusername.send_keys('bob')
        passwordbox = self.browser.find_element_by_id('id_password')
        passwordbox.send_keys('bob')
        submitbutton = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/h3[2]/form/input[2]')
        submitbutton.send_keys(Keys.ENTER)
        # Dr. Makes sure that it is titled correctly
        self.assertIn('Assessment System', self.browser.title)

        # Dr. chooses a semester from a drop down list
        semester_header_text = self.browser.find_element_by_id('semester').text
        self.assertIn("Choose a Semester!", semester_header_text)
        semester_dropdown = self.browser.find_element_by_id('semesterdropdown')
        self.assertEqual(semester_dropdown.get_attribute('name'), "semester")
        semesterchoice = self.browser.find_elements_by_tag_name('option')
        self.assertIn('201530', [i.text for i in semesterchoice])

        # Dr. clicks submit to send a post request to a server
        submitbutton = self.browser.find_element_by_id('semestersubmit')
        self.assertEqual(submitbutton.get_attribute('value'), "Submit")
        submitbutton.send_keys(Keys.ENTER)

        ##Future funtional test for choosing a semester
        # Dr. is given the option to choose a class
        header_text = self.browser.find_element_by_id('edclass').text
        self.assertIn("Choose a Class!", header_text)

        # Dr. Chooses a class from a list of classes
        dropdown_list = self.browser.find_element_by_id('classdropdown')
        self.assertEqual(dropdown_list.get_attribute('name'), "edClass")
        classchoice = self.browser.find_elements_by_tag_name('option')
        self.assertIn("EG 5000 01", [i.text for i in classchoice])
        #sleep(60)
        # Dr. clicks on a "Choose" button and is taken to a new page
        submitbutton = self.browser.find_element_by_id('classubmit')
        submitbutton.send_keys(Keys.ENTER)

        # If there is more than one assignment, Dr. Chooses an assignment
        assignmentchoice = self.browser.find_elements_by_tag_name('option')
        self.assertIn("Writing Assignment", [i.text for i in assignmentchoice])
        writingassignment = self.browser.find_element_by_id('Writing Assignment')
        writingassignment.click()
        submitbutton = self.browser.find_element_by_id('assignmentsubmit')
        submitbutton.send_keys(Keys.ENTER)

        chooseAStudent = self.browser.find_element_by_id('choosename')
        # Dr. chooses a student name from a drop down list of student names
        studentnamedropdown = self.browser.find_element_by_id('studentdropdown')
        self.assertEqual(studentnamedropdown.get_attribute('name'), 'studentnames')
        studentname = self.browser.find_elements_by_tag_name('option')
        self.assertIn("Bob DaBuilder 21743148", [i.text for i in studentname])
        self.assertIn("Jane Doe 21743149", [i.text for i in studentname])
        submitbuttonstudent = self.browser.find_element_by_id('studentsubmit')
        submitbuttonstudent.send_keys(Keys.ENTER)

        # A new page should appear with the student's name
        studentnameheader = self.browser.find_element_by_id('studentheader')
        self.assertIn("DaBuilder, Bob", studentnameheader.text)

        # A rubric should appear based upon the key assignment with row names
        rubricheader = self.browser.find_element_by_id('rubricheader')
        self.assertIn("Writing Rubric", rubricheader.text)
        bodytext = self.browser.find_element_by_tag_name('body')
        self.assertIn("Excellence is a habit", bodytext.text)  # row name should stil be there
        self.assertIn("THE BEST!", bodytext.text)

        # The rubric should allow the professor to click on a matrix of rows

        row1dropdown = self.browser.find_element_by_id('id_form-0-row_choice')
        row2dropdown = self.browser.find_element_by_id('id_form-1-row_choice')
        self.assertEqual(row1dropdown.get_attribute('name'), 'form-0-row_choice')
        self.assertEqual(row2dropdown.get_attribute('name'), 'form-1-row_choice')

        rubricoptions = self.browser.find_elements_by_tag_name('option')

        self.assertIn("Exemplary", [option.text for option in rubricoptions])
        excellent = self.browser.find_element_by_xpath('//*[@id="id_form-0-row_choice"]/option[3]')
        excellent.click()

        # The dr. clicks on "submit" the student data is submitted to a database
        submitbutton = self.browser.find_element_by_id('rubricsubmit')
        submitbutton.send_keys(Keys.ENTER)
        bodytext = self.browser.find_element_by_tag_name('body')
        self.assertIn("Excellence is a habit", bodytext.text) #row name should stil be there
        self.assertIn("THE BEST!", bodytext.text)

        # Dr. discoveres that empty values are not accepted in the rubric
        bodytext = self.browser.find_element_by_tag_name('body')
        self.assertIn("You must choose a value for all rows!", bodytext.text)

        # Dr. decides to fill out the entire rubric this time
        proficient = self.browser.find_element_by_xpath('//*[@id="id_form-1-row_choice"]/option[3]')
        proficient.click()
        submitbutton = self.browser.find_element_by_id('rubricsubmit')
        submitbutton.send_keys(Keys.ENTER)

        # Clicking submit should save rubric and return to the main student page
        studentnamedropdown = self.browser.find_element_by_id('studentdropdown')
        self.assertEqual(studentnamedropdown.get_attribute('name'), 'studentnames')

        # Dr. chooses a different name and fills out a COMPLETELY new rubric
        studentnames = self.browser.find_elements_by_tag_name('option')
        janedoe = self.browser.find_element_by_id('21743149')
        janedoe.click()
        submitbuttonstudent = self.browser.find_element_by_id('studentsubmit')
        submitbuttonstudent.send_keys(Keys.ENTER)
        excellent = self.browser.find_element_by_xpath('//*[@id="id_form-0-row_choice"]/option[2]')

        # First choice should not be excellent it should be null
        # self.assertNotEqual(excellent.get_attribute("selected"), "true")
        excellent = self.browser.find_element_by_xpath('//*[@id="id_form-0-row_choice"]/option[2]')
        excellent.click()
        proficient = self.browser.find_element_by_xpath('//*[@id="id_form-1-row_choice"]/option[3]')
        proficient.click()
        submitbuttonstudent = self.browser.find_element_by_id('rubricsubmit')
        submitbuttonstudent.send_keys(Keys.ENTER)

        # The new webpage should say "No more students"
        bodytext = self.browser.find_element_by_tag_name('body')
        self.assertIn("There are no more students", bodytext.text)

        # Dr. returns to the class page and chooses different assignment
        self.browser.get("%s%s" % (self.server_url, '/assessment/201530/EG500001/'))
        assignmentchoice = self.browser.find_elements_by_tag_name('option')
        self.assertIn("Unit Assignment", [i.text for i in assignmentchoice])
        unitassignment = self.browser.find_element_by_id('Unit Assignment')
        unitassignment.click()
        submitbutton = self.browser.find_element_by_id('assignmentsubmit')
        submitbutton.send_keys(Keys.ENTER)

        # Dr. sees two student rubrics that are available to complete
        studentnamedropdown = self.browser.find_element_by_id('studentdropdown')
        self.assertEqual(studentnamedropdown.get_attribute('name'), 'studentnames')
        studentname = self.browser.find_elements_by_tag_name('option')
        self.assertIn("Bob DaBuilder 21743148", [i.text for i in studentname])
        self.assertIn("Jane Doe 21743149", [i.text for i in studentname])

        # Dr. chooses a student
        bob = self.browser.find_element_by_id('21743148')
        bob.click()
        submitbuttonstudent = self.browser.find_element_by_id('studentsubmit')
        submitbuttonstudent.send_keys(Keys.ENTER)

        # Dr. completes the rubric

        excellent = self.browser.find_element_by_xpath('//*[@id="id_form-0-row_choice"]/option[2]')
        excellent.click()
        #proficient = self.browser.find_element_by_xpath('//*[@id="id_form-1-row_choice"]/option[3]')
        #proficient.click()
        submitbuttonstudent = self.browser.find_element_by_id('rubricsubmit')
        submitbuttonstudent.send_keys(Keys.ENTER)

        # Dr. returns to assignment page to see that completed student is not there
        studentnamedropdown = self.browser.find_element_by_id('studentdropdown')
        self.assertEqual(studentnamedropdown.get_attribute('name'), 'studentnames')
        studentname = self.browser.find_elements_by_tag_name('option')
        self.assertNotIn("Bob DaBuilder 21743148", [i.text for i in studentname])
        self.assertIn("Jane Doe 21743149", [i.text for i in studentname])

        # Dr. chooses Jane Doe
        jane = self.browser.find_element_by_id('21743149')
        jane.click()
        submitbuttonstudent = self.browser.find_element_by_id('studentsubmit')
        submitbuttonstudent.send_keys(Keys.ENTER)

        #Dr. completes rubric
        excellent = self.browser.find_element_by_xpath('//*[@id="id_form-0-row_choice"]/option[2]')
        excellent.click()
        #proficient = self.browser.find_element_by_xpath('//*[@id="id_form-1-row_choice"]/option[3]')
        #proficient.click()
        submitbuttonstudent = self.browser.find_element_by_id('rubricsubmit')
        submitbuttonstudent.send_keys(Keys.ENTER)

        #Dr. returns to the student page.  There should be no more students
        bodytext = self.browser.find_element_by_tag_name('body')
        self.assertIn("There are no more students", bodytext.text)

        # The mischevious professor tries to go back to a completed student url
        unit = Assignment.objects.get(assignmentname="Unit Assignment")
        self.browser.get("%s%s" % (self.server_url, '/assessment/201530/EG500001/unitassignment{}/21743148'.format(unit.pk)))
        bodytext = self.browser.find_element_by_tag_name('body')
        self.assertIn("You have already completed a rubric for this student.", bodytext.text)

        # nonplussed, they return home
        home = self.browser.find_element_by_link_text("Return Home")
        home.click()
        semester_header_text = self.browser.find_element_by_id('semester').text
        self.assertIn("Choose a Semester!", semester_header_text)
		
		#
        self.browser.get(self.server_url + '/user/')
        sleep(60)


