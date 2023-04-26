from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from rubricapp.models import Semester, EdClasses, Student, Enrollment, Rubric, Row, Assignment, RubricData,Standard
from time import sleep
from django.contrib.auth.models import User
from django.test.utils import override_settings
from django.conf import settings


class DataView(FunctionalTest):
    def create_enrollment_for_student(self, edclassescrn, lnumber):
        student = Student.objects.get(lnumber=lnumber)
        for i in edclassescrn:
            edclassobj = EdClasses.objects.get(crn=i)
            Enrollment.objects.create(student=student, edclass=edclassobj)

    def createrubricrow(self, name,excellenttext, rubric, row_choice, standardpassed, templatename):
        rowname = Row.objects.create(name=name,
                                     excellenttext=excellenttext,
                                     proficienttext="THE SECOND BEST!",
                                     satisfactorytext="THE THIRD BEST!",
                                     unsatisfactorytext="YOU'RE LAST", rubric=rubric, row_choice=row_choice, templatename=templatename)
        rowname.standards.add(standardpassed)

        return rowname


    def create_two_classes_for_unit_tests(self):
        semester = Semester.objects.create(text="201530")
        semester2 = Semester.objects.create(text="201610")
        edclass1 = EdClasses.objects.create(sectionnumber="01", subject="EG", coursenumber="5000",
                                            teacher=self.test_user, crn=2222, semester=semester)
        edclass2 = EdClasses.objects.create(sectionnumber="01", subject="EG", coursenumber="6000",
                                            teacher=self.test_user, crn=3333, semester=semester)


        bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
        jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")
        jake = Student.objects.create(lastname="The Snake", firstname="Jake", lnumber="0000")

        self.create_enrollment_for_student([2222, 3333], "21743148")
        self.create_enrollment_for_student([2222, 3333], "21743149")

        intasc1 = Standard.objects.create(name="INTASC 1")
        caep1 = Standard.objects.create(name="CAEP 1")

        writingrubric = Rubric.objects.create(name="writingrubric")

        row1 = self.createrubricrow("Excellence","THE BEST!",writingrubric, 0, intasc1, "writingrubric")
        row2 = self.createrubricrow("NONE", "THE GREATEST!", writingrubric,0, caep1, "writingrubric")

        # Many to many relationship must be added after creation of objects
        # because the manyto-many relationship is not a column in the database
        #writingassignment.keyrubric.add(writingrubric)
        #unitplan.keyrubric.add(writingrubric)
        writingassignment = Assignment.objects.create(edclass=edclass1, assignmentname="Writing Assignment", keyrubric=writingrubric)
        unitplan = Assignment.objects.create(edclass=edclass1, assignmentname="Unit Plan", keyrubric=writingrubric)

        completedrubricforbobwriting = Rubric.objects.create( name="EG50000121743148201530WritingAssignment4", template=False)
        row1 = self.createrubricrow("Excellence", "THE BEST!", completedrubricforbobwriting, 1, intasc1, "writingrubric")
        row2 = self.createrubricrow("None", "THE GREATEST!", completedrubricforbobwriting, 1, caep1, "writingrubric")

        completedrubricforbobunit = Rubric.objects.create(name="EG50000121743148201530UnitPlan5", template=False)
        row1 = self.createrubricrow("Excellence", "THE BEST!", completedrubricforbobunit, 4, intasc1, "writingrubric")
        row2 = self.createrubricrow("None", "THE GREATEST!", completedrubricforbobunit, 4, caep1, "writingrubric")

        bobenrollment = Enrollment.objects.get(edclass=edclass1, student=bob)
        RubricData.objects.create(assignment=writingassignment, enrollment=bobenrollment, rubriccompleted=True, completedrubric=completedrubricforbobwriting)
        RubricData.objects.create(assignment=unitplan, enrollment=bobenrollment, rubriccompleted=True, completedrubric=completedrubricforbobunit)

    def create_more_student_data_for_second_test(self):
        semester201610 = Semester.objects.get(text="201610")
        EG9000201610 = EdClasses.objects.create(sectionnumber="01", subject="EG", coursenumber="9000",
                                            teacher=self.test_user, crn=5555, semester=semester201610)

        communicationrubric = Rubric.objects.create(name="communicationrubric")
        communicationplan = Assignment.objects.create(edclass=EG9000201610,assignmentname="Communication Plan", keyrubric=communicationrubric)
        intasc1 = Standard.objects.get(name="INTASC 1")
        caep1 = Standard.objects.get(name="CAEP 1")

        row1 = self.createrubricrow("Skills","STUPDENDOUS!",communicationrubric, 0, intasc1, "communicationrubric")
        row2 = self.createrubricrow("Karate", "AMAZING!", communicationrubric, 0, intasc1, "communicationrubric")

        jake = Student.objects.get(lastname="The Snake")

        jakeenrollment = Enrollment.objects.create(edclass=EG9000201610, student=jake)
        completedrubricforjakecommunication = Rubric.objects.create(name="EG9000010000CommunicationPlan6", template=False)
        row1 = self.createrubricrow("Skills","STUPDENDOUS!",completedrubricforjakecommunication, 3, intasc1,"communicationrubric")
        row2 = self.createrubricrow("Karate", "AMAZING!", completedrubricforjakecommunication, 3, intasc1, "communicationrubric")

        RubricData.objects.create(assignment=communicationplan, enrollment=jakeenrollment,rubriccompleted=True, completedrubric=completedrubricforjakecommunication)


    def test_professor_visits_the_main_page(self):

        # Professor pulls up the data view
        self.create_two_classes_for_unit_tests()
        self.browser.get("%s%s" % (self.server_url, '/data/'))
        # Prof must first login to the assessment system
        idusername = self.browser.find_element_by_id('id_username')
        idusername.send_keys('bob')
        passwordbox = self.browser.find_element_by_id('id_password')
        passwordbox.send_keys('bob')
        submitbutton = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/h3[2]/form/input[2]')
        submitbutton.send_keys(Keys.ENTER)
        ##TODO logging takes user back to assessmentpage
        self.browser.get("%s%s" % (self.server_url, '/data/'))
        # Prof finds several options for how to view rubrics
        headertext = self.browser.find_element_by_id('headertext')
        self.assertEquals(headertext.text, "Choose a data retrieval method")
        studentchoice = self.browser.find_element_by_id('studentlink')
        self.assertEquals(studentchoice.text, "Look at one student's rubrics")
        classchoice = self.browser.find_element_by_id('classlink')
        self.assertEquals(classchoice.text, "Look at aggregated class data")

        # Professor Chooses the student view
        studentchoice.click()
        studentchoiceheader = self.browser.find_element_by_id("studentchoice")
        self.assertEqual(studentchoiceheader.text, "Choose a student!")

        # Professor Encounters a magical drop down menu with student names
        studentdropdown = self.browser.find_element_by_id('studentnames')
        self.assertEqual(studentdropdown.get_attribute('name'), 'studentnames')
        studentname = self.browser.find_elements_by_tag_name('option')
        self.assertIn("Bob DaBuilder 21743148", [i.text for i in studentname])
        submitbuttonstudent = self.browser.find_element_by_id('studentsubmit')
        submitbuttonstudent.send_keys(Keys.ENTER)

        # Professor chooses a rubric
        studentnameheader = self.browser.find_element_by_tag_name('h3')
        self.assertIn("Bob DaBuilder", studentnameheader.text)
        rubricnames = self.browser.find_elements_by_tag_name('option')
        self.assertIn("EG50000121743148201530WritingAssignment4", [i.text for i in rubricnames])
        self.assertIn("EG50000121743148201530UnitPlan5", [i.text for i in rubricnames])
        submitbuttonstudent = self.browser.find_element_by_id('rubricsubmit')
        submitbuttonstudent.send_keys(Keys.ENTER)

        # Professor sees the rubric
        bodytext = self.browser.find_element_by_tag_name('body')
        self.assertIn("Excellence", bodytext.text)

        # Prof changes their minds.  They want to look at all the rubrics from a particular course
        self.browser.get("%s%s" % (self.server_url, '/data/'))
        classchoice = self.browser.find_element_by_id('classlink')
        classchoice.click()

        # Prof must choose by a semester.  OH MY
        semesterdropdown = self.browser.find_element_by_id('semesterselectid')
        semesternames = self.browser.find_elements_by_tag_name('option')
        self.assertIn('201530', [i.text for i in semesternames])
        submitbutton = self.browser.find_element_by_id('semestersubmit')
        submitbutton.send_keys(Keys.ENTER)

        # Prof sees that there is a class there
        classdropdown = self.browser.find_element_by_id('edlcassdropdown')
        self.assertEqual(classdropdown.get_attribute('name'), 'edclass')
        classnames = self.browser.find_elements_by_tag_name('option')
        self.assertIn("EG 5000 01", [i.text for i in classnames])
        submitbutton = self.browser.find_element_by_id('classsubmit')
        submitbutton.send_keys(Keys.ENTER)

        # The following page should show a list of assignments
        bodytext = self.browser.find_element_by_tag_name('body')
        self.assertIn("Writing Assignment", bodytext.text)
        self.assertIn("Unit Plan", bodytext.text)
        submitbutton = self.browser.find_element_by_id('assignmentsubmit')
        submitbutton.send_keys(Keys.ENTER)

        # The next page should show the completed rubric for the class
        bodytext = self.browser.find_element_by_tag_name('body')
        #http://localhost:8081/data/class/201530/EG500001/unitplan5/
        self.assertIn("Excellence", bodytext.text)
        self.assertIn("1", bodytext.text)

        # Professor needs to look at unit plan, but goes to wrong course
        self.browser.get("%s%s" % (self.server_url, '/data/class/201530/EG600001/'))
        bodytext = self.browser.find_element_by_tag_name('body')
        self.assertIn("There are no assignments for this course", bodytext.text)

        # Professor goes to right url and sees Unit Plan Rubric rubric there
        self.browser.get("{}{}".format(self.server_url, '/data/class/201530/EG5000001/'))
        unitplandrop = self.browser.find_element_by_name('Unit Plan')
        unitplandrop.click()
        submitbutton = self.browser.find_element_by_id('assignmentsubmit')
        submitbutton.send_keys(Keys.ENTER)

        #1.0 Should not be in the body of this text.  That is the writing assignment.
        #However 4.0 should be in the assignment because it is the correct rubric.
        bodytext = self.browser.find_element_by_tag_name('body')
        self.assertNotIn("1.0", bodytext.text)
        self.assertIn("4.0", bodytext.text)

        # Professor Decides to go back to the home page
        self.assertIn("Return to data home", bodytext.text)
        self.browser.find_element_by_link_text('Return to data home').click()

    def test_professor_looks_at_data_for_multiple_students(self):
        self.create_two_classes_for_unit_tests()
        self.create_more_student_data_for_second_test()
        self.browser.get("%s%s" % (self.server_url, '/data/'))
        # Prof must first login to the assessment system
        idusername = self.browser.find_element_by_id('id_username')
        idusername.send_keys('bob')
        passwordbox = self.browser.find_element_by_id('id_password')
        passwordbox.send_keys('bob')
        submitbutton = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/h3[2]/form/input[2]')
        submitbutton.send_keys(Keys.ENTER)

        ##TODO logging takes user back to assessmentpage
        self.browser.get("%s%s" % (self.server_url, '/data/'))
        # Prof finds several options for how to view rubrics
        headertext = self.browser.find_element_by_id('headertext')
        self.assertEquals(headertext.text, "Choose a data retrieval method")
        studentchoice = self.browser.find_element_by_id('studentlink')
        self.assertEquals(studentchoice.text, "Look at one student's rubrics")
        classchoice = self.browser.find_element_by_id('classlink')
        self.assertEquals(classchoice.text, "Look at aggregated class data")
        classchoice.click()

        # Prof must choose by a semester.  OH MY
        semesterdropdown = self.browser.find_element_by_id('semesterselectid')
        semesternames = self.browser.find_elements_by_tag_name('option')
        self.assertIn('201610', [i.text for i in semesternames])
        submitbutton = self.browser.find_element_by_id('semestersubmit')
        semester201610 = self.browser.find_element_by_xpath('//*[@id="semesterselectid"]/option[2]')
        semester201610.click()
        submitbutton.send_keys(Keys.ENTER)

        # Prof sees that there is a class there
        classdropdown = self.browser.find_element_by_id('edlcassdropdown')
        self.assertEqual(classdropdown.get_attribute('name'), 'edclass')
        classnames = self.browser.find_elements_by_tag_name('option')
        self.assertIn("EG 9000 01", [i.text for i in classnames])
        submitbutton = self.browser.find_element_by_id('classsubmit')
        submitbutton.send_keys(Keys.ENTER)

        # The following page should show a list of assignments
        bodytext = self.browser.find_element_by_tag_name('body')
        self.assertIn("Communication Plan", bodytext.text)
        submitbutton = self.browser.find_element_by_id('assignmentsubmit')
        submitbutton.send_keys(Keys.ENTER)

        # The next page should show one score
        bodytext = self.browser.find_element_by_tag_name('body')
        self.assertIn("Karate", bodytext.text)
        self.assertIn("3.0", bodytext.text)

        # Professor returns to the main data page and clicks on standards link
        self.browser.get("{}{}".format(self.server_url, '/data/'))
        standardslink = self.browser.find_element_by_id('standardslink')
        standardslink.click()

        #Professor checks to see if the 201530 Intasc Page has
        #Correct numbers
        bodyofpage = self.browser.find_element_by_tag_name('body')
        self.assertIn('201530', bodyofpage.text)
        submit = self.browser.find_element_by_id('standardsubmit')
        submit.click()
        intascinpage = self.browser.find_element_by_xpath('//*[@id="INTASC"]')
        self.assertIn('INTASC 1', intascinpage.text)
        intascinpage.click()
        submit = self.browser.find_element_by_id('standardsubmit')
        submit.click()
        bodyofpage = self.browser.find_element_by_tag_name('body')
        self.assertIn("Excellence", bodyofpage.text)
        self.assertIn("2.5", bodyofpage.text)

        #Professor visits the 201530 caep page.
        self.browser.get("{}{}".format(self.server_url, '/data/standards/'))
        submit = self.browser.find_element_by_id("standardsubmit")
        submit.click()
        caep1 = self.browser.find_element_by_xpath('//*[@id="standardsname"]/option[1]')
        self.assertIn("CAEP 1", caep1.text)
        sleep(60)
        caep1.click()
        submit = self.browser.find_element_by_id('standardsubmit')
        submit.click()
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn("None", body.text)
        self.assertIn("2.50", body.text)

        #Professor visits 20160 page
        self.browser.get("{}{}".format(self.server_url, '/data/standards/'))
        semester2016 = self.browser.find_element_by_xpath('//*[@id="semestername"]/option[2]')
        self.assertIn("201610", semester2016.text)
        semester2016.click()
        submit = self.browser.find_element_by_id('standardsubmit')
        submit.click()
        intasc1 = self.browser.find_element_by_xpath('//*[@id="INTASC"]')
        self.assertIn("INTASC 1", intasc1.text)
        submit = self.browser.find_element_by_id('standardsubmit')
        submit.click()
        self.browser.get("{}{}".format(self.server_url, '/data/standards/201610/intasc1/'))
        body = self.browser.find_element_by_tag_name("body")
        self.assertIn('3.0',body.text)
        self.assertIn("Karate",body.text)
        self.assertIn("Skills", body.text)

        #Professor wonders what rubric rows are associated with which standard
        self.browser.get("{}{}".format(self.server_url, '/data/standards/rubricview'))
        intasc1 = self.browser.find_element_by_tag_name('body')
        self.assertIn("INTASC 1", intasc1.text)
        submit = self.browser.find_element_by_id('standardsubmit')
        submit.click()
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn("writingrubric", body.text)
        ##TODO FINISH






