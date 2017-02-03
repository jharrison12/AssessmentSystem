from django.test import TestCase, Client
from unittest import skip
from django.core.urlresolvers import resolve
from dataview.views import home_page, student_view, student_data_view, ed_class_view, ed_class_data_view, \
    semester_ed_class_view, ed_class_assignment_view
from rubricapp.models import Semester, Student, Enrollment, EdClasses, Rubric, Row, Assignment, RubricData
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
        unitplan = Assignment.objects.create(edclass=edclass1, assignmentname="Unit Plan")  # , semester=semester)
        writingassignment = Assignment.objects.create(edclass=edclass2,
                                                      assignmentname="Writing Assignment")  # , semester=semester)

        # semester.classes.add(edclass1)
        # semester.classes.add(edclass2)

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

        # Many to many relationship must be added after creation of objects
        # because the manyto-many relationship is not a column in the database
        # edclass1.keyrubric.add(writingrubric)
        # edclass2.keyrubric.add(writingrubric)
        unitplan.keyrubric.add(writingrubric)
        writingassignment.keyrubric.add(writingrubric)

        completedrubricforbob = Rubric.objects.create(name="EG50000121743148201530", template=False)
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
        bobenrollmentrubricdata = RubricData.objects.get_or_create(enrollment=bobenrollment, assignment=unitplan, rubriccompleted=True)
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
        self.assertIn("EG50000121743148201530", response.content.decode())

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
        response = self.client.get('/data/student/21743148/EG50000121743148201530/')
        self.assertIn("Rubric", response.content.decode())

    def test_student_rubric_view_uses_correct_template(self):
        response = self.client.get('/data/student/21743148/EG50000121743148201530/')
        self.assertTemplateUsed(response, 'dataview/studentrubricview.html')

    def test_student_rubric_view_shows__rows(self):
        response = self.client.get('/data/student/21743148/EG50000121743148201530/')
        self.assertIn("Excellenceisahabit", response.content.decode())

    def test_student_rubric_view_shows_scores(self):
        response = self.client.get('/data/student/21743148/EG50000121743148201530/')
        self.assertIn("Incomplete", response.content.decode())

    def test_student_rubic_view_requires_login(self):
        self.client.logout()
        response = self.client.get('/data/student/21743148/EG50000121743148201530/')
        self.assertRedirects(response, '/login/?next=/data/student/21743148/EG50000121743148201530/', status_code=302)

    def test_student_rubric_view_requires_superuser(self):
        self.client.logout()
        kathy = User.objects.create_user(username="kathy", password="b")
        istrue = self.client.login(username="kathy", password="b")
        self.assertEquals(istrue, True)
        response = self.client.get("/data/student/21743148/EG50000121743148201530/")
        self.assertRedirects(response, '/login/?next=/data/student/21743148/EG50000121743148201530/', status_code=302)

    def test_student_does_not_appear_if_zero_tests(self):
        ron = Student.objects.create(lastname="Smith", firstname="Ron", lnumber="21111111")
        response = self.client.get('/data/student/')
        self.assertNotIn("Ron Smith", response.content.decode())


class EdClass(TestCase):
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
        writingassignmentfirst = Assignment.objects.create(edclass=edclass1,
                                                           assignmentname="Writing Assignment")  # , semester=semester)
        writingassignmentsecond = Assignment.objects.create(edclass=edclass2,
                                                            assignmentname="Leader Paper")  # , semester=semester)
        writingassignmentthird = Assignment.objects.create(edclass=edclass3,
                                                           assignmentname="Nonleader paper")  # m semester=semester2)
        writingassignmentfourth = Assignment.objects.create(edclass=edclass4,
                                                            assignmentname="Loser Paper")  # , semester=semester2)


        """
        -->201530

        ---->Eg 5000 05

        ------->Writing Assignment
        ----------> Bob, Jane

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

        # semester.classes.add(edclass1)
        # semester.classes.add(edclass2)

        bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
        jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")
        jake = Student.objects.create(lastname="The Snake", firstname="Jake", lnumber="0000")

        bobenrollment = Enrollment.objects.create(student=bob, edclass=edclass1)  # , semester=semester)
        bobenrollment1 = Enrollment.objects.create(student=bob, edclass=edclass2)  # , semester=semester)
        janeenrollment = Enrollment.objects.create(student=jane, edclass=edclass4)  # , semester=semester)
        janeenrollment2 = Enrollment.objects.create(student=jane, edclass=edclass2)  # , semester=semester)
        jakeenrollment = Enrollment.objects.create(student=jake, edclass=edclass3)  # , semester=semester2)
        writingrubric = Rubric.objects.create(name="writingrubric")

        row1 = Row.objects.create(name="Fortitude",
                                  excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=writingrubric)

        row2 = Row.objects.create(name="Excellenceisahabit",
                                  excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=writingrubric)

        # Many to many relationship must be added after creation of objects
        # because the manyto-many relationship is not a column in the database
        # edclass1.keyrubric.add(writingrubric)
        # edclass2.keyrubric.add(writingrubric)
        writingassignmentfirst.keyrubric.add(writingrubric)
        writingassignmentsecond.keyrubric.add(writingrubric)
        writingassignmentthird.keyrubric.add(writingrubric)
        writingassignmentfourth.keyrubric.add(writingrubric)

        completedrubricforbob = Rubric.objects.create(name="EG50000121743148201530", template=False)
        row1 = Row.objects.create(name="Fortitude",
                                  excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedrubricforbob, row_choice=2)

        row2 = Row.objects.create(name="Excellenceisahabit",
                                  excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedrubricforbob, row_choice=4)

        bobenrollment.completedrubric = completedrubricforbob
        #bobenrollment.rubriccompleted = True
        bobenrollment.save()

        completedrubricforbobeg6000 = Rubric.objects.create(name="EG600021743148201530", template=False)
        row1 = Row.objects.create(name="Fortitude",
                                  excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedrubricforbobeg6000, row_choice=1)

        row2 = Row.objects.create(name="Excellenceisahabit",
                                  excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedrubricforbobeg6000, row_choice=1)
        bobenrollment1.completedrubric = completedrubricforbobeg6000
        bobenrollment1.save()

        completedrubricforjane = Rubric.objects.create(name="EG50000121743149201530", template=False)
        row1 = Row.objects.create(name="Fortitude",
                                  excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedrubricforjane, row_choice=1)

        row2 = Row.objects.create(name="Excellenceisahabit",
                                  excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedrubricforjane, row_choice=1)

        janeenrollment.completedrubric = completedrubricforjane
        #janeenrollment.rubriccompleted = True
        janeenrollment.save()

        completedrubricforjake = Rubric.objects.create(name="EG5000010000201610", template=False)
        row1 = Row.objects.create(name="Fortitude",
                                  excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedrubricforjake, row_choice=4)
        row2 = Row.objects.create(name="Excellenceisahabit",
                                  excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=completedrubricforjake, row_choice=4)

        jakeenrollment.completedrubric = completedrubricforjake
        #jakeenrollment.rubriccompleted = True
        jakeenrollment.save()
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
        response = self.client.get("/data/class/201530/%s/" % (edclass))
        self.assertTemplateUsed(response, 'dataview/classassignmentdataview.html')

    def test_class_data_page_uses_correct_template(self):
        edclass = EdClasses.objects.get(subject="EG", coursenumber="5000", sectionnumber="05", semester__text="201530")
        edclass = re.sub('[\s+]', '', str(edclass))
        assignment = Assignment.objects.get(assignmentname="Writing Assignment")
        response = self.client.get(
            "/data/class/201530/%s/%s%s/" % (edclass, assignment.assignmentname.replace(' ', ''), assignment.pk))
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
        response = self.client.get('/data/class/201530/EG500005/writingassignment1/')
        self.assertIn("2.0", response.content.decode())

    def test_EG500005_201610_rubric_data_does_not_appear_in_wrong_semester(self):
        response = self.client.get('/data/class/201610/EG500005/writingassignment1/')
        self.assertNotIn("1.5", response.content.decode())
        self.assertNotIn("2.5", response.content.decode())

    def test_EG500005_201610_rubric_shows_only_jake_score(self):
        assignment = Assignment.objects.get(assignmentname="Nonleader paper")
        response = self.client.get('/data/class/201610/EG500005/{}{}/'.format("nonleaderpaper",assignment.pk))
        # should only show score of 4.0
        self.assertIn("4.0", response.content.decode())

    def test_EG6000_201530_rubric_shows_only_one_score(self):
        response = self.client.get('/data/class/201530/EG600004/writingassignment1/')
        self.assertIn("1.0", response.content.decode())

    def test_same_class_different_semester_different_rubric_data(self):

        twentyseventeen = Semester.objects.create(text="201710")
        kelly = User.objects.get(username="kelly")
        edclass = EdClasses.objects.create(subject="EG", coursenumber="5000", sectionnumber="05", semester=twentyseventeen,
                                           crn=0000, teacher=kelly)
        hugeleaderpaper = Assignment.objects.create(edclass=edclass, assignmentname="Huge leader paper")
        completedrubricforgeorge = Rubric.objects.create(name="EG500001555201710", template=False)
        hugeleaderpaper.keyrubric.add(completedrubricforgeorge)
        badrow = Row.objects.create(excellenttext="STOP",
                                    proficienttext="STOP",
                                    satisfactorytext="STOP",
                                    unsatisfactorytext="STOP", rubric=completedrubricforgeorge, row_choice=3)

        george = Student.objects.create(lastname="Harrison", firstname="George", lnumber="5555")
        georgeenrollment = Enrollment.objects.create(student=george, edclass=edclass)  # ,semester=twentyseventeen)
        georgeenrollment.completedrubric = completedrubricforgeorge
        georgeenrollment.rubriccompleted = True
        georgeenrollment.save()
        response = self.client.get('/data/class/201710/EG500005/hugeleaderpaper{}/'.format(hugeleaderpaper.pk))
        self.assertContains(response, "3.0")

    def test_EG6000_201530_rubric_only_shows_two_decimal_places(self):
        summer2016 = Semester.objects.get(text="201530")
        edclass = EdClasses.objects.get(subject="EG", coursenumber="6000", sectionnumber="04", semester=summer2016)
        edclasssemester = Assignment.objects.filter(edclass=edclass)
        completedrubricforgeorge = Rubric.objects.create(name="EG6000045555201530", template=False)
        # edclasssemester.keyrubric.add(completedrubricforgeorge)

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
        georgeenrollment.completedrubric = completedrubricforgeorge
        georgeenrollment.rubriccompleted = True
        georgeenrollment.save()

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
        harryenrollment.completedrubric = completedrubricforharry
        harryenrollment.rubriccompleted = True
        harryenrollment.save()

        response = self.client.get('/data/class/201530/EG600004/')
        self.assertNotIn("2.666", response.content.decode())

    def test_class_data_view_shows_same_class_different_assignment(self):
        eg5000 = EdClasses.objects.get(crn=2222)
        semester= Semester.objects.get(text='201530')
        unitplan = Assignment.objects.create(edclass=eg5000, assignmentname="Unit Plan")
        unitrubric = Rubric.objects.create(name="unitrubric")

        row1 = Row.objects.create(excellenttext="UNIT PLAN!",
                                  proficienttext="UNIQUE!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=unitrubric)

        row2 = Row.objects.create(excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST", rubric=unitrubric)

        unitplan.keyrubric.add(unitrubric)

        completedunitrubricforbob = Rubric.objects.create(name="EG50000121743148201530Unit", template=False)
        row1 = Row.objects.create(name="Fortitude",
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

        bobenrollment.completedrubric = completedunitrubricforbob
        bobenrollment.save()

        request = HttpRequest()
        request.method = "POST"
        request.user = self.test_user

        bobenrollmentrubricdata = RubricData.objects.get_or_create(enrollment=bobenrollment, assignment=unitplan, rubriccompleted=True)
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


