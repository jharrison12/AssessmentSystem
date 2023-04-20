from django.test import TestCase, Client
from unittest import skip
from django.urls import resolve
from dataview.views import home_page, student_view, student_data_view, ed_class_view, ed_class_data_view, \
    semester_ed_class_view, ed_class_assignment_view, standards_view, standards_semester_view, standards_semester_standard_view,\
    rubric_standard_view, rubric_standard_individual_view

from rubricapp.views import rubric_page
from rubricapp.models import Semester, Student, Enrollment, EdClasses, Rubric, Row, Assignment, RubricData, Standard
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
        login = self.client.login(username=self.username, password=self.password)

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
        self.assertRedirects(response, '/login/?next=/data/', status_code=302)

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
        edclass1 = EdClasses.objects.create(subject="EG", coursenumber="5000", teacher=jacob, crn=2222,
                                            sectionnumber="01", semester=semester)
        edclass2 = EdClasses.objects.create(subject="EG", coursenumber="6000", teacher=jacob, crn=3333,
                                            sectionnumber="01", semester=semester)

        bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
        jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")
        jake = Student.objects.create(lastname="The Snake", firstname="Jake", lnumber="0000")

        bobenrollment = Enrollment.objects.create(student=bob, edclass=edclass1)  # , semester=semester)
        bobenrollment1 = Enrollment.objects.create(student=bob, edclass=edclass2)  # , semester=semester)
        janeenrollment = Enrollment.objects.create(student=jane, edclass=edclass1)  # , semester=semester)
        janeenrollment2 = Enrollment.objects.create(student=jane, edclass=edclass2)  # , semester=semester)
        writingrubric = Rubric.objects.create(name="writingrubric")

        row1 = Row.objects.create(excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=writingrubric)

        row2 = Row.objects.create(excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=writingrubric)
        unitplan = Assignment.objects.create(edclass=edclass1, assignmentname="Unit Plan", keyrubric=writingrubric)  # , semester=semester)
        writingassignment = Assignment.objects.create(edclass=edclass2,
                                                      assignmentname="Writing Assignment", keyrubric=writingrubric)
        # Many to many relationship must be added after creation of objects
        # because the manyto-many relationship is not a column in the database
        # edclass1.keyrubric.add(writingrubric)
        # edclass2.keyrubric.add(writingrubric)
        #unitplan.keyrubric.add(writingrubric)
        #writingassignment.keyrubric.add(writingrubric)

        completedrubricforbob = Rubric.objects.create(name="EG50000121743148201530UnitPlan", template=False)
        row1 = Row.objects.create(name="Fortitude",
                                  excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedrubricforbob, row_choice=2)

        row2 = Row.objects.create(name="Excellenceisahabit",
                                  excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedrubricforbob, row_choice=1)

        bobenrollment.completedrubric = completedrubricforbob
        # TODO Complete this below
        bobenrollmentrubricdata = RubricData.objects.get_or_create(enrollment=bobenrollment, assignment=unitplan, rubriccompleted=True, completedrubric=completedrubricforbob)
        bobenrollmentrubricdata1 = RubricData.objects.get_or_create(enrollment=bobenrollment1, assignment=writingassignment, rubriccompleted=True)
        bobenrollment.save()
        self.client = Client()
        self.username = 'bob'
        self.email = 'test@test.com'
        self.password = 'test'
        self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
        login = self.client.login(username=self.username, password=self.password)

    def test_student_appears_only_once(self):
        response = self.client.get('/data/student/')
        numbob = re.findall("Bob", response.content.decode())
        self.assertEquals(len(numbob), 1)

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
        # follow=True follows the redirect to the login page
        response = self.client.get("/data/student/")
        self.assertIn("Bob DaBuilder", response.content.decode())

    def test_student_page_shows_multiple_students(self):
        jane = Student.objects.get(lastname="Doe")
        edclass1 = EdClasses.objects.get(crn=2222)
        janeenrollment = Enrollment.objects.get(student=jane, edclass=edclass1)
        unitplan = Assignment.objects.get(assignmentname="Unit Plan")
        completedrubricforjane = Rubric.objects.create(name="EG50000121743149201530UnitPlan", template=False)
        RubricData.objects.create(enrollment=janeenrollment, assignment=unitplan, rubriccompleted=True, completedrubric=completedrubricforjane)
        janeenrollment.save()
        response = self.client.get("/data/student/")
        self.assertIn("Jane Doe", response.content.decode())

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
        kathy = User.objects.create_user(username="kathy", password="b")
        istrue = self.client.login(username="kathy", password="b")
        self.assertEquals(istrue, True)
        response = self.client.get('/data/student/21743148/')
        self.assertRedirects(response, '/login/?next=/data/student/21743148/', status_code=302)

    def test_dataview_page_exists_for_bob(self):
        response = self.client.get('/data/student/21743148/')
        self.assertIn("Bob", response.content.decode())

    def test_data_view_shows_rubrics(self):
        response = self.client.get('/data/student/21743148/')
        self.assertIn("EG50000121743148201530UnitPlan", response.content.decode())

    def test_student_data_page_has_submit_button(self):
        response = self.client.get("/data/student/21743148/")
        self.assertIn("Submit", response.content.decode())

    def test_student_data_view_takes_post_request(self):
        request = HttpRequest()
        request.method = "POST"
        request.POST['rubricname'] = "bobcompletedrubric"
        request.user = self.test_user
        response = student_data_view(request, lnumber="21743148")
        self.assertEqual(response.status_code, 302)

    def test_student_data_view_redirects_to_correct_url(self):
        request = HttpRequest()
        request.method = "POST"
        request.POST['rubricname'] = "EG500001 21743148 201530"
        request.user = self.test_user
        response = student_data_view(request, lnumber="21743148")
        self.assertEqual(response['location'], 'EG50000121743148201530/')

    def test_student_rubric_view_shows_a_rubric(self):
        response = self.client.get('/data/student/21743148/EG50000121743148201530UnitPlan/')
        self.assertIn("Rubric", response.content.decode())

    def test_student_rubric_view_uses_correct_template(self):
        response = self.client.get('/data/student/21743148/EG50000121743148201530UnitPlan/')
        self.assertTemplateUsed(response, 'dataview/studentrubricview.html')

    def test_student_rubric_view_shows__rows(self):
        response = self.client.get('/data/student/21743148/EG50000121743148201530UnitPlan/')
        self.assertIn("Excellenceisahabit", response.content.decode())

    def test_student_rubric_view_shows_scores(self):
        response = self.client.get('/data/student/21743148/EG50000121743148201530UnitPlan/')
        self.assertIn("Incomplete", response.content.decode())

    def test_student_rubic_view_requires_login(self):
        self.client.logout()
        response = self.client.get('/data/student/21743148/EG50000121743148201530UnitPlan/')
        self.assertRedirects(response, '/login/?next=/data/student/21743148/EG50000121743148201530UnitPlan/', status_code=302)

    def test_student_rubric_view_requires_superuser(self):
        self.client.logout()
        kathy = User.objects.create_user(username="kathy", password="b")
        istrue = self.client.login(username="kathy", password="b")
        self.assertEquals(istrue, True)
        response = self.client.get("/data/student/21743148/EG50000121743148201530UnitPlan/")
        self.assertRedirects(response, '/login/?next=/data/student/21743148/EG50000121743148201530UnitPlan/', status_code=302)

    def test_student_does_not_appear_if_zero_tests(self):
        ron = Student.objects.create(lastname="Smith", firstname="Ron", lnumber="21111111")
        response = self.client.get('/data/student/')
        self.assertNotIn("Ron Smith", response.content.decode())


class EdClass(TestCase):
    def createrubricrow(self, name,excellenttext, rubric, row_choice):
        rowname = Row.objects.create(name=name,
                                     excellenttext=excellenttext,
                                     proficienttext="THE SECOND BEST!",
                                     satisfactorytext="THE THIRD BEST!",
                                     unsatisfactorytext="YOU'RE LAST", rubric=rubric, row_choice=row_choice )
        return rowname

    def setUp(self):
        semester = Semester.objects.create(text="201530")
        semester2 = Semester.objects.create(text="201610")
        kelly = User.objects.create(username="kelly")
        edclass1 = EdClasses.objects.create(sectionnumber="05", subject="EG", coursenumber="5000", teacher=kelly,
                                            crn=2222, semester=semester)
        edclass3 = EdClasses.objects.create(sectionnumber="05", subject="EG", coursenumber="5000", teacher=kelly,
                                            crn=9999, semester=semester2)
        edclass2 = EdClasses.objects.create(sectionnumber="04", subject="EG", coursenumber="6000", teacher=kelly,
                                            crn=3333, semester=semester2)
        edclass4 = EdClasses.objects.create(sectionnumber="04", subject="EG", coursenumber="6000", teacher=kelly,
                                            crn=8888, semester=semester)



        """
        -->201530

        ---->Eg 5000 05

        ------->Writing Assignment
        ----------> Bob

        ---->EG 6000 04
        ------->Loser Paper

        -->201610

        ---->EG 5000 05
        ------->Nonleader Ppaer
        ----------> Jake


        ---->EG 6000 04
        ------->Leader Paper
        ----------> Bob, Jane
        """

        bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
        jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")
        jake = Student.objects.create(lastname="The Snake", firstname="Jake", lnumber="0000")

        bobenrollment = Enrollment.objects.create(student=bob, edclass=edclass1)  # , semester=semester)
        bobenrollment1 = Enrollment.objects.create(student=bob, edclass=edclass2)  # , semester=semester)
        janeenrollment = Enrollment.objects.create(student=jane, edclass=edclass4)  # , semester=semester)
        janeenrollment2 = Enrollment.objects.create(student=jane, edclass=edclass2)  # , semester=semester)
        jakeenrollment = Enrollment.objects.create(student=jake, edclass=edclass3)  # , semester=semester2)
        writingrubric = Rubric.objects.create(name="writingrubric")

        row1 = self.createrubricrow("Fortitude", "THE BEST!", writingrubric,0)
        row2 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!", writingrubric,0)

        writingassignmentfirst = Assignment.objects.create(edclass=edclass1,
                                                           assignmentname="Writing Assignment", keyrubric=writingrubric)  # , semester=semester)
        writingassignmentsecond = Assignment.objects.create(edclass=edclass2,
                                                            assignmentname="Leader Paper", keyrubric=writingrubric)  # , semester=semester)
        writingassignmentthird = Assignment.objects.create(edclass=edclass3,
                                                           assignmentname="Nonleader paper", keyrubric=writingrubric)  # m semester=semester2)
        writingassignmentfourth = Assignment.objects.create(edclass=edclass4,
                                                            assignmentname="Loser Paper", keyrubric=writingrubric)  # , semester=semester2)

        # Many to many relationship must be added after creation of objects
        # because the manyto-many relationship is not a column in the database

        #writingassignmentfirst.keyrubric.add(writingrubric)
        #writingassignmentsecond.keyrubric.add(writingrubric)
        #writingassignmentthird.keyrubric.add(writingrubric)
        #writingassignmentfourth.keyrubric.add(writingrubric)

        #Create EG 6000 04 Jane, Leader Paper
        completedrubricforEG600004Jane = Rubric.objects.create(name="EG60000421743149201610LeaderPaper", template=False)
        row1 = self.createrubricrow("Fortitude", "THE BEST!", completedrubricforEG600004Jane, 4)
        row2 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!", completedrubricforEG600004Jane, 4)
        RubricData.objects.create(enrollment=janeenrollment2, assignment=writingassignmentsecond, rubriccompleted=True, completedrubric=completedrubricforEG600004Jane)

        #Create EG 6000 04 Bob, LeaderPaper
        completedrubricforEG600004Bob = Rubric.objects.create(name="EG60000421743148201610LeaderPaper", template=False)
        row1 = self.createrubricrow("Fortitude", "THE BEST!", completedrubricforEG600004Bob, 1)
        row2 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!", completedrubricforEG600004Bob, 3)
        RubricData.objects.create(enrollment=bobenrollment1, assignment=writingassignmentsecond, rubriccompleted=True, completedrubric=completedrubricforEG600004Bob)

        #Create EG 5000 05 Bob, Writing Assignment
        completedrubricforbob = Rubric.objects.create(name="EG50000521743148201530WritingAssignment", template=False)
        row1 = self.createrubricrow("Fortitude","THE BEST!",completedrubricforbob,2)
        row2 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!", completedrubricforbob, 4)
        RubricData.objects.create(enrollment=bobenrollment, assignment=writingassignmentfirst, rubriccompleted=True, completedrubric=completedrubricforbob)

        #Create EG 6000 04 Loser Paper
        completedrubricforjaneEG6000 = Rubric.objects.create(name="EG60000421743148201530LoserPaper", template=False)
        row1 = self.createrubricrow("Fortitude", "THE BEST!", completedrubricforjaneEG6000, 1)
        row2 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!", completedrubricforjaneEG6000, 1)
        RubricData.objects.create(enrollment=janeenrollment, assignment=writingassignmentfourth, rubriccompleted=True, completedrubric=completedrubricforjaneEG6000)

        completedrubricforjane = Rubric.objects.create(name="EG50000121743149201530WritingAssignment", template=False)
        row1 = self.createrubricrow("Fortitude", "THE BEST!", completedrubricforjane, 1)
        row2 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!", completedrubricforjane, 1)
        RubricData.objects.create(enrollment=janeenrollment, assignment=writingassignmentfirst, rubriccompleted=True, completedrubric=completedrubricforjane)

        completedrubricforjake = Rubric.objects.create(name="EG5000010000201610", template=False)
        row1 = self.createrubricrow("Fortitude", "THE BEST!", completedrubricforjake, 4)
        row1 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!!", completedrubricforjake, 4)
        RubricData.objects.create(enrollment=jakeenrollment, assignment=writingassignmentthird, rubriccompleted=True, completedrubric=completedrubricforjake)

        self.client = Client()
        self.username = 'bob'
        self.email = 'test@test.com'
        self.password = 'test'
        self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
        login = self.client.login(username=self.username, password=self.password)

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
        # follow=True follows the redirect to the login page
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
        request.POST['edclass'] = "EG 5000 01"
        response = ed_class_view(request, "201530")
        self.assertEqual(response['location'], "EG500001/")

    def test_class_data_page_returns_correct_function(self):
        found = resolve('/data/class/201530/EG500001/')
        self.assertEqual(found.func, ed_class_assignment_view)

    def test_class_data_page_returns_correct_function(self):
        found = resolve('/data/class/201530/EG500001/writingassignment1/')
        self.assertEqual(found.func, ed_class_data_view)

    def test_class_assignment_page_uses_correct_template(self):
        edclass = EdClasses.objects.get(subject="EG", coursenumber="5000", sectionnumber="05", semester__text="201530")
        edclass = re.sub('[\s+]', '', str(edclass))
        response = self.client.get("/data/class/201530/EG500005/")
        self.assertTemplateUsed(response, 'dataview/classassignmentdataview.html')

    def test_class_data_page_uses_correct_template(self):
        edclass = EdClasses.objects.get(subject="EG", coursenumber="5000", sectionnumber="05", semester__text="201530")
        edclass = re.sub('[\s+]', '', str(edclass))
        assignment = Assignment.objects.get(assignmentname="Writing Assignment")
        response = self.client.get(
            "/data/class/201530/EG500005/{}{}/".format(assignment.assignmentname.replace(' ', ''), assignment.pk))
        self.assertTemplateUsed(response, 'dataview/classdataview.html')

    def test_class_assignment_page_requires_login(self):
        self.client.logout()
        response = self.client.get('/data/class/201530/EG500001/')
        self.assertRedirects(response, '/login/?next=/data/class/201530/EG500001/', status_code=302)

    def test_class_assignment_data_page_requires_login(self):
        self.client.logout()
        response = self.client.get('/data/class/201530/EG500001/writingassignment1/')
        self.assertRedirects(response, '/login/?next=/data/class/201530/EG500001/writingassignment1/', status_code=302)

    def test_semester_class_data_view_requires_superuser_login(self):
        self.client.logout()
        kathy = User.objects.create_user(username="kathy", password="b")
        istrue = self.client.login(username="kathy", password="b")
        self.assertEquals(istrue, True)
        response = self.client.get('/data/class/201530/EG500001/')
        self.assertRedirects(response, '/login/?next=/data/class/201530/EG500001/', status_code=302)

    def test_class_rubric_view_shows_assignment(self):
        response = self.client.get('/data/class/201530/EG500005/')
        self.assertIn("Writing Assignment", response.content.decode())

    def test_class_data_page_shows_aggregated_score(self):
        response = self.client.get('/data/class/201610/EG600004/leaderpaper2/')
        self.assertIn("2.5", response.content.decode())
        self.assertIn("3.5", response.content.decode())

    def test_EG500005_201610_rubric_data_does_not_appear_in_wrong_semester(self):
        response = self.client.get('/data/class/201610/EG500005/nonleaderpaper3/')
        self.assertNotIn("1.5", response.content.decode())
        self.assertNotIn("2.5", response.content.decode())

    def test_EG500005_201610_rubric_shows_only_jake_score(self):
        assignment = Assignment.objects.get(assignmentname="Nonleader paper")
        response = self.client.get('/data/class/201610/EG500005/{}{}/'.format("nonleaderpaper",assignment.pk))
        # should only show score of 4.0
        self.assertIn("4.0", response.content.decode())

    def test_EG6000_201530_rubric_shows_only_one_score(self):
        response = self.client.get('/data/class/201530/EG600004/loserpaper4/')
        self.assertIn("1.0", response.content.decode())

    def test_same_class_different_semester_different_rubric_data(self):

        twentyseventeen = Semester.objects.create(text="201710")
        kelly = User.objects.get(username="kelly")
        edclass = EdClasses.objects.create(subject="EG", coursenumber="5000", sectionnumber="05", semester=twentyseventeen,
                                           crn=0000, teacher=kelly)
        blankrubric = Rubric.objects.create()
        hugeleaderpaper = Assignment.objects.create(edclass=edclass, assignmentname="Huge leader paper", keyrubric=blankrubric)
        completedrubricforgeorge = Rubric.objects.create(name="EG500001555201710", template=False)
        #hugeleaderpaper.keyrubric.add(completedrubricforgeorge)
        badrow = Row.objects.create(excellenttext="STOP",
                                    proficienttext="STOP",
                                    satisfactorytext="STOP",
                                    unsatisfactorytext="STOP", rubric=completedrubricforgeorge, row_choice=3)

        george = Student.objects.create(lastname="Harrison", firstname="George", lnumber="5555")
        georgeenrollment = Enrollment.objects.create(student=george, edclass=edclass)  # ,semester=twentyseventeen)

        RubricData.objects.create(enrollment=georgeenrollment, assignment=hugeleaderpaper, rubriccompleted=True, completedrubric=completedrubricforgeorge)
        response = self.client.get('/data/class/201710/EG500005/hugeleaderpaper{}/'.format(hugeleaderpaper.pk))
        self.assertContains(response, "3.0")

    def test_EG6000_201530_rubric_only_shows_two_decimal_places(self):
        summer2016 = Semester.objects.get(text="201530")
        edclass = EdClasses.objects.get(subject="EG", coursenumber="6000", sectionnumber="04", semester=summer2016)
        edclasssemester = Assignment.objects.filter(edclass=edclass)
        completedrubricforgeorge = Rubric.objects.create(name="EG6000045555201530", template=False)

        row1 = Row.objects.create(name="Fortitude",
                                  excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedrubricforgeorge, row_choice=4)

        row2 = Row.objects.create(name="Excellenceisahabit",
                                  excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedrubricforgeorge, row_choice=4)

        george = Student.objects.create(lastname="Harrison", firstname="George", lnumber="5555")
        georgeenrollment = Enrollment.objects.create(student=george, edclass=edclass)  # ,semester=summer2016)

        completedrubricforharry = Rubric.objects.create(name="EG6000044444201530", template=False)

        row1 = Row.objects.create(name="Fortitude",
                                  excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedrubricforharry, row_choice=3)

        row2 = Row.objects.create(name="Excellenceisahabit",
                                  excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedrubricforharry, row_choice=3)

        harry = Student.objects.create(lastname="Harrison", firstname="Harry", lnumber="4444")
        harryenrollment = Enrollment.objects.create(student=harry, edclass=edclass)  # ,semester=summer2016)

        response = self.client.get('/data/class/201530/EG600004/')
        self.assertNotIn("2.666", response.content.decode())

    def test_class_data_view_shows_same_class_different_assignment(self):
        eg5000 = EdClasses.objects.get(crn=2222)
        semester= Semester.objects.get(text='201530')

        unitrubric = Rubric.objects.create(name="unitrubric")

        row1 = Row.objects.create(excellenttext="UNIT PLAN!",
                                  proficienttext="UNIQUE!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=unitrubric)

        row2 = Row.objects.create(excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=unitrubric)
        unitplan = Assignment.objects.create(edclass=eg5000, assignmentname="Unit Plan", keyrubric=unitrubric)
        #unitplan.keyrubric.add(unitrubric)

        completedunitrubricforbob = Rubric.objects.create(name="EG50000121743148201530Unit", template=False)
        row1 = Row.objects.create(name="UNIQUE",
                                  excellenttext="UNIT PLAN!",
                                  proficienttext="UNIQUE!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedunitrubricforbob, row_choice=2)

        row2 = Row.objects.create(name="Excellenceisahabit",
                                  excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedunitrubricforbob, row_choice=1)

        bobenrollment = Enrollment.objects.get(student__lnumber="21743148", edclass__crn=2222)

        request = HttpRequest()
        request.method = "POST"
        request.user = self.test_user

        bobenrollmentrubricdata = RubricData.objects.get_or_create(enrollment=bobenrollment, assignment=unitplan, rubriccompleted=True, completedrubric=completedunitrubricforbob)
        response = ed_class_data_view(request,edclass="EG500005", semester="201530",assignmentname="{}".format(unitplan.pk) )
        self.assertIn("UNIQUE", response.content.decode())

    def test_class_page_can_take_post_request(self):
        request = HttpRequest()
        request.method = "POST"
        request.user = self.test_user
        request.POST['assignment'] = "Writing Assignment"
        response = ed_class_assignment_view(request, "EG500005" ,"201530")
        self.assertEqual(response.status_code, 302)

    def test_class_page_redirects_to_right_page(self):
        request = HttpRequest()
        request.method = "POST"
        request.user = self.test_user
        request.POST['assignment'] = "Writing Assignment"
        response = ed_class_assignment_view(request, "EG500005", "201530")
        self.assertEqual(response['location'], 'writingassignment1/')

    def test_two_assignments_in_the_same_class(self):
        semester = Semester.objects.get(text="201610")
        eg500005201610 = EdClasses.objects.get(semester=semester, crn=9999)

        jakeenrollment = Enrollment.objects.get(student__lastname="The Snake", edclass=eg500005201610)

        lessonplanrubric = Rubric.objects.create(name="lessonplanrubric")
        lessonplan = Assignment.objects.create(assignmentname="Lesson Plan",edclass=eg500005201610, keyrubric=lessonplanrubric)
        row1 = self.createrubricrow("Fortitude", "THE BEST!", lessonplanrubric,0)
        row2 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!", lessonplanrubric,0)

        #lessonplan.keyrubric.add(lessonplanrubric)

        completedrubricforjakelessonplan = Rubric.objects.create(name="EG5000050000201610", template=False)
        row1 = self.createrubricrow("Fortitude", "THE BEST!", completedrubricforjakelessonplan, 1)
        row1 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!!", completedrubricforjakelessonplan, 1)
        RubricData.objects.create(enrollment=jakeenrollment, assignment=lessonplan, rubriccompleted=True, completedrubric=completedrubricforjakelessonplan)

        response = self.client.get('/data/class/201610/EG500005/lessonplan{}/'.format(lessonplan.pk))
        self.assertNotIn('4', response.content.decode())

    def test_two_assignments_in_the_same_class_using_same_rubric(self):
        semester = Semester.objects.get(text="201610")
        eg500005201610 = EdClasses.objects.get(semester=semester, crn=9999)

        jakeenrollment = Enrollment.objects.get(student__lastname="The Snake", edclass=eg500005201610)

        writingrubric = Rubric.objects.get(name="writingrubric")
        lessonplan = Assignment.objects.create(assignmentname="Lesson Plan",edclass=eg500005201610, keyrubric=writingrubric)
        #lessonplan.keyrubric.add(writingrubric)

        completedrubricforjakelessonplan = Rubric.objects.create(name="EG5000050000201610", template=False)
        row1 = self.createrubricrow("Fortitude", "THE BEST!", completedrubricforjakelessonplan, 1)
        row1 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!!", completedrubricforjakelessonplan, 1)
        RubricData.objects.create(enrollment=jakeenrollment, assignment=lessonplan, rubriccompleted=True, completedrubric=completedrubricforjakelessonplan)

        response = self.client.get('/data/class/201610/EG500005/lessonplan{}/'.format(lessonplan.pk))
        self.assertNotIn('4', response.content.decode())


class StandardView(TestCase):

    def createrubricrow(self, name, excellenttext, rubric, row_choice, standard, templatename):
        rowname = Row.objects.create(name=name,
                                     excellenttext=excellenttext,
                                     proficienttext="THE SECOND BEST!",
                                     satisfactorytext="THE THIRD BEST!",
                                     unsatisfactorytext="YOU'RE LAST", rubric=rubric, row_choice=row_choice, templatename=templatename.name)
        rowname.standards.add(standard)
        rowname.save()
        return rowname


    def setUp(self):
        intasc1 = Standard.objects.create(name='INTASC 1')
        caep1 = Standard.objects.create(name="CAEP 1.2")
        empty = Standard.objects.create(name=" ")
        semester201530 = Semester.objects.create(text="201530")
        semester201610 = Semester.objects.create(text="201610")

        kelly = User.objects.create(username="kelly")
        EG500005201530 = EdClasses.objects.create(sectionnumber="05", subject="EG", coursenumber="5000", teacher=kelly,
                                            crn=2222, semester=semester201530)
        EG500005201610 = EdClasses.objects.create(sectionnumber="05", subject="EG", coursenumber="5000", teacher=kelly,
                                            crn=9999, semester=semester201610)
        EG600004201610 = EdClasses.objects.create(sectionnumber="04", subject="EG", coursenumber="6000", teacher=kelly,
                                            crn=3333, semester=semester201610)
        EG600004201530 = EdClasses.objects.create(sectionnumber="04", subject="EG", coursenumber="6000", teacher=kelly,
                                            crn=8888, semester=semester201530)

        """
        -->201530

        ---->Eg 5000 05

        ------->Writing Assignment
        ----------> Bob

        ---->EG 6000 04
        ------->Loser Paper
        ----------> Jane

        -->201610

        ---->EG 5000 05
        ------->Nonleader Ppaer
        ----------> Jake


        ---->EG 6000 04
        ------->Leader Paper
        ----------> Bob, Jane
        """

        bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
        jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")
        jake = Student.objects.create(lastname="The Snake", firstname="Jake", lnumber="0000")

        bobEG500005201530 = Enrollment.objects.create(student=bob, edclass=EG500005201530)  # , semester=semester)
        bobEG600004201610 = Enrollment.objects.create(student=bob, edclass=EG600004201610)  # , semester=semester)
        janeEG600004201530 = Enrollment.objects.create(student=jane, edclass=EG600004201530)  # , semester=semester)
        janeEG600004201610 = Enrollment.objects.create(student=jane, edclass=EG600004201610)  # , semester=semester)
        jakeEG500005201610 = Enrollment.objects.create(student=jake, edclass=EG500005201610)  # , semester=semester2)
        writingrubric = Rubric.objects.create(name="Writing Rubric")

        row1 = self.createrubricrow("Fortitude", "THE BEST!", writingrubric, 0, intasc1, writingrubric)
        row2 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!", writingrubric, 0,caep1,writingrubric)

        writingassignment = Assignment.objects.create(edclass=EG500005201530,
                                                           assignmentname="Writing Assignment",
                                                           keyrubric=writingrubric)  # , semester=semester)
        leaderpaper = Assignment.objects.create(edclass=EG600004201610,
                                                            assignmentname="Leader Paper",
                                                            keyrubric=writingrubric)  # , semester=semester)
        nonleaderpaper = Assignment.objects.create(edclass=EG500005201610,
                                                           assignmentname="Nonleader paper",
                                                           keyrubric=writingrubric)  # m semester=semester2)
        loserpaper = Assignment.objects.create(edclass=EG600004201530,
                                                            assignmentname="Loser Paper",
                                                            keyrubric=writingrubric)  # , semester=semester2)

        # Many to many relationship must be added after creation of objects
        # because the manyto-many relationship is not a column in the database

        # Create EG 5000 05 201610
        completedrubricforjake = Rubric.objects.create(name="EG5000050000201610", template=False)
        row1 = self.createrubricrow("Fortitude", "THE BEST!", completedrubricforjake, 4, intasc1, writingrubric)
        row1 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!!", completedrubricforjake, 4, caep1,writingrubric)
        RubricData.objects.create(enrollment=jakeEG500005201610, assignment=nonleaderpaper, rubriccompleted=True,
                                  completedrubric=completedrubricforjake)

        # Create EG 6000 04 Jane, Leader Paper 201610

        completedrubricforEG600004Jane = Rubric.objects.create(name="EG60000421743149201610LeaderPaper", template=False)
        row1 = self.createrubricrow("Fortitude", "THE BEST!", completedrubricforEG600004Jane, 4, intasc1,writingrubric)
        row2 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!", completedrubricforEG600004Jane, 4, caep1,writingrubric)
        RubricData.objects.create(enrollment=janeEG600004201610, assignment=leaderpaper, rubriccompleted=True,
                                  completedrubric=completedrubricforEG600004Jane)

        # Create EG 6000 04 Bob, LeaderPaper 201610
        completedrubricforEG600004Bob = Rubric.objects.create(name="EG60000421743148201610LeaderPaper", template=False)
        row1 = self.createrubricrow("Fortitude", "THE BEST!", completedrubricforEG600004Bob, 1, intasc1,writingrubric)
        row2 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!", completedrubricforEG600004Bob, 3, caep1,writingrubric)
        RubricData.objects.create(enrollment=bobEG600004201610, assignment=leaderpaper, rubriccompleted=True,
                                  completedrubric=completedrubricforEG600004Bob)

        # Create EG 5000 05 Bob, Writing Assignment 201530
        completedrubricforbob = Rubric.objects.create(name="EG50000521743148201530WritingAssignment", template=False)
        row1 = self.createrubricrow("Fortitude", "THE BEST!", completedrubricforbob, 2, intasc1,writingrubric)
        row2 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!", completedrubricforbob, 4, caep1,writingrubric)
        RubricData.objects.create(enrollment=bobEG500005201530, assignment=writingassignment, rubriccompleted=True,
                                  completedrubric=completedrubricforbob)

        # Create EG 6000 04 Loser Paper 201530
        completedrubricforjaneeg6000 = Rubric.objects.create(name="EG60000421743149201530LoserPaper", template=False)
        row1 = self.createrubricrow("Fortitude", "THE BEST!", completedrubricforjaneeg6000, 1, intasc1,writingrubric)
        row2 = self.createrubricrow("Excellenceisahabit", "THE GREATEST!", completedrubricforjaneeg6000, 1, caep1,writingrubric)
        RubricData.objects.create(enrollment=janeEG600004201530, assignment=loserpaper, rubriccompleted=True,
                                  completedrubric=completedrubricforjaneeg6000)

        self.client = Client()
        self.username = 'bob'
        self.email = 'test@test.com'
        self.password = 'test'
        self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
        login = self.client.login(username=self.username, password=self.password)

    def test_data_view_home_has_standard_link(self):
        response = self.client.get('/data/')
        self.assertContains(response, "standards data", status_code=200)

    def test_standard_view_requires_login(self):
        self.client.logout()
        response = self.client.get('/data/standards/')
        self.assertRedirects(response, '/login/?next=/data/standards/', status_code=302)

    def test_standard_view_uses_standard_view_function(self):
        found = resolve('/data/standards/')
        self.assertEqual(found.func, standards_view)

    def test_standards_view_home(self):
        response = self.client.get('/data/standards/')
        self.assertContains(response, 'Standards', status_code=200)

    def test_standard_view_uses_correct_template(self):
        response = self.client.get('/data/standards/')
        self.assertTemplateUsed(response, 'dataview/standardsview.html')

    def test_standards_view_shows_a_semester(self):
        response = self.client.get('/data/standards/')
        self.assertContains(response, '201530')

    def test_standards_view_shows_rubric_option(self):
        response = self.client.get('/data/standards/')
        self.assertContains(response, 'See what rubrics use what standards')

    def test_standards_view_can_take_post_request(self):
        request = HttpRequest()
        request.method = "POST"
        request.user = self.test_user
        request.POST['semestername'] = "201530"
        response = standards_view(request)
        self.assertEqual(response.status_code, 302)

    def test_standards_semester_requires_loing(self):
        self.client.logout()
        response = self.client.get('/data/standards/201530/')
        self.assertRedirects(response, '/login/?next=/data/standards/201530/', status_code=302)

    def test_standards_semester_page_uses_correct_function(self):
        found = resolve('/data/standards/201530/')
        self.assertEqual(found.func, standards_semester_view)

    def test_standards_semester_page_has_standards(self):
        response = self.client.get('/data/standards/201530/')
        self.assertContains(response, "INTASC 1", status_code=200)

    def test_standard_view_uses_correct_template(self):
        response = self.client.get('/data/standards/201530/')
        self.assertTemplateUsed(response, 'dataview/standardssemesterview.html')

    def test_standards_semester_page_takes_post(self):
        request = HttpRequest()
        request.method = "POST"
        request.user = self.test_user
        request.POST['standardsname'] = "INTASC 1"
        response = standards_semester_view(request, "201530")
        self.assertEqual(response.status_code, 302)

    def test_semester_standards_redirects_correctly(self):
        response = self.client.post('/data/standards/201530/',{'standardsname': "INTASC 1"})
        self.assertRedirects(response, '/data/standards/201530/intasc1/')

    def test_standards_semester_standard_view_uses_correct_template(self):
        response = self.client.get('/data/standards/201530/intasc1/')
        self.assertTemplateUsed(response, 'dataview/standardssemesterstandardview.html')

    def test_standards_semester_standard_view_uses_correct_function(self):
        found = resolve('/data/standards/201530/intasc1/')
        self.assertEqual(found.func, standards_semester_standard_view)

    def test_standards_semester_standard_view_requires_loing(self):
        self.client.logout()
        response = self.client.get('/data/standards/201530/intasc1/')
        self.assertRedirects(response, '/login/?next=/data/standards/201530/intasc1/', status_code=302)

    def test_sss_page_has_standard_name(self):
        response = self.client.get('/data/standards/201530/intasc1/')
        self.assertIn("INTASC 1",response.content.decode())

    def test_sss_page_shows_rubric(self):
        response = self.client.get('/data/standards/201530/intasc1/')
        self.assertIn("Writing Rubric", response.content.decode())

    def test_sss_page_shows_scores(self):
        response = self.client.get('/data/standards/201530/intasc1/')
        self.assertIn("1.5", response.content.decode())

    def test_sss_page_shows_scores(self):
        response  = self.client.get('/data/standards/201530/caep1.2/')
        self.assertIn("2.50", response.content.decode())

    def test_sss_page_shows_scores(self):
        response  = self.client.get('/data/standards/201610/caep1.2/')
        self.assertIn("3.67", response.content.decode())

    def test_sss_page_works_with_multiple_rubrics(self):
        intasc1 = Standard.objects.get(name='INTASC 1')
        caep1 = Standard.objects.get(name="CAEP 1.2")
        semester201530 = Semester.objects.get(text="201530")
        semester201610 = Semester.objects.get(text="201610")
        kelly = User.objects.get(username="kelly")
        EG700005201530 = EdClasses.objects.create(sectionnumber="05", subject="EG", coursenumber="7000", teacher=kelly,
                                                  crn=5555, semester=semester201530)

        bob = Student.objects.get(lastname="DaBuilder", firstname="Bob", lnumber="21743148")

        bobEG700005201530 = Enrollment.objects.create(student=bob, edclass=EG700005201530)  # , semester=semester)
        unitrubric = Rubric.objects.create(name="Unit Rubric")

        unitassignment = Assignment.objects.create(edclass=EG700005201530,
                                                      assignmentname="Unit Assignment",
                                                      keyrubric=unitrubric)  # , semester=semester)

        # Create EG 7000 05 201530
        completedrubricforbob = Rubric.objects.create(name="EG70000521743148201530", template=False)
        self.createrubricrow("Fortitude", "THE BEST!", completedrubricforbob, 3, intasc1, unitrubric)
        self.createrubricrow("Excellenceisahabit", "THE GREATEST!!", completedrubricforbob, 4, caep1,
                                    unitrubric)
        RubricData.objects.create(enrollment=bobEG700005201530, assignment=unitassignment, rubriccompleted=True,
                                     completedrubric=completedrubricforbob)

        response = self.client.get('/data/standards/201530/intasc1/')
        self.assertIn("Unit Rubric", response.content.decode())
        self.assertIn("3.0", response.content.decode())

    def test_standards_rubric_view_uses_correct_view_function(self):
        found = resolve('/data/standards/rubricview/')
        self.assertEqual(found.func, rubric_standard_view)

    def test_standards_rubric_view_shows_standard(self):
        response = self.client.get('/data/standards/rubricview/')
        self.assertContains(response, 'INTASC 1', status_code=200)

    def test_standards_rubric_view_requires_login(self):
        self.client.logout()
        response = self.client.get('/data/standards/rubricview/')
        self.assertRedirects(response, '/login/?next=/data/standards/rubricview/', status_code=302)

    def test_standard_rubric_view_uses_correct_template(self):
        response = self.client.get('/data/standards/rubricview/')
        self.assertTemplateUsed(response, 'dataview/rubricstandardview.html')

    def test_standard_rubric_view_takes_post(self):
        request = HttpRequest()
        request.method = "POST"
        request.user = self.test_user
        request.POST['standardselect'] = "INTASC 1"
        response = rubric_standard_view(request)
        self.assertEqual(response.status_code, 302)

    def test_standard_rubric_view_redirects_to_correct_page(self):
        request = HttpRequest()
        request.method = "POST"
        request.user = self.test_user
        request.POST["standardselect"] = "INTASC 1"
        response = rubric_standard_view(request)
        self.assertEqual(response['location'], 'intasc1/')

    def test_intasc_rubric_view_uses_correct_function(self):
        found = resolve('/data/standards/rubricview/instasc1/')
        self.assertEqual(found.func, rubric_standard_individual_view)

    def test_instasc_standards_rubric_view_requires_login(self):
        self.client.logout()
        response = self.client.get('/data/standards/rubricview/intasc1/')
        self.assertRedirects(response, '/login/?next=/data/standards/rubricview/intasc1/', status_code=302)

    def test_intasc_rubric_view_uses_correct_template(self):
        response = self.client.get('/data/standards/rubricview/instasc1/')
        self.assertTemplateUsed(response, 'dataview/rubricstandardindividual.html')

    def test_intasc_rubric_view_shows_writing(self):
        response = self.client.get('/data/standards/rubricview/intasc1/')
        self.assertIn("Writing Rubric", response.content.decode())

    def test_intasc_rubric_view_with_more_rubrics(self):
        intasc1 = Standard.objects.get(name="INTASC 1")
        newrubric = Rubric.objects.create(name="Unit Rubric", template=True)
        self.createrubricrow("Excellence is a Habit", "THE BEST!", newrubric, 0, intasc1, newrubric)
        response = self.client.get("/data/standards/rubricview/intasc1/")
        self.assertIn("Unit Rubric", response.content.decode())
        self.assertIn("Excellence is a Habit", response.content.decode())

    def test_intasc_rubric_view_with_more_rubrics_with_multiple_rows(self):
        intasc1 = Standard.objects.get(name="INTASC 1")
        newrubric = Rubric.objects.create(name="Unit Rubric", template=True)
        self.createrubricrow("Excellence is a Habit", "THE BEST!", newrubric, 0, intasc1, newrubric)
        self.createrubricrow("Mediocrity is a habit", "THE BEST!", newrubric, 0, intasc1, newrubric)
        response = self.client.get("/data/standards/rubricview/intasc1/")
        self.assertIn("Mediocrity is a habit", response.content.decode())

    def test_rubric_with_row_with_multi_standards_works(self):
        #add intasc to second row
        intasc1 = Standard.objects.get(name="INTASC 1")
        caeprow = Row.objects.get(name="Excellenceisahabit", rubric__template=True)
        caeprow.standards.add(intasc1)
        response = self.client.get("/data/standards/rubricview/intasc1/")
        self.assertIn("Excellenceisahabit", response.content.decode())

    def test_caep_standard_with_period_works(self):
        response = self.client.get('/data/standards/rubricview/caep1.2/')
        self.assertContains(response, 'Excellenceisahabit', status_code=200)


