from unittest import skip
from rubricapp.models import Semester, EdClasses, Student, Enrollment, Rubric, Row, Assignment,RubricData
from django.template.loader import render_to_string
from django.http import HttpRequest
from django.test import TestCase, Client
from rubricapp.views import home_page, semester_page, student_page, rubric_page, user_page, assignment_page
from django.core.urlresolvers import resolve
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
    @skip
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
        edclass1 = EdClasses.objects.create(sectionnumber="01", subject="EG", coursenumber="5111", teacher=jane, crn=2222, semester=semester)
        #semester.classes.add(edclass1)
        edclasssemester = Assignment.objects.create(edclass=edclass1)
        response = self.client.get('/assessment/201530/')
        self.assertNotIn("EG 5111", response.content.decode())

    def test_bob_can_see_bob_class(self):
        semester = Semester.objects.create(text="201530")
        jane = User.objects.create(username="Jane")
        rubric = Rubric.objects.create(name="BOB")
        edclass1 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="5111", teacher=self.test_user, crn=2222, semester=semester)
        edclasssemester = Assignment.objects.create(edclass=edclass1)#, keyrubric=rubric)
        edclasssemester.keyrubric.add(rubric)
        #semester.classes.add(edclass1)
        response = self.client.get('/assessment/201530/')
        self.assertIn("EG 5111", response.content.decode())

    def test_displays_all_classes(self):
        semester = Semester.objects.create(text="201530")
        rubric = Rubric.objects.create(name="BOB")
        edclass1 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="5000", teacher=self.test_user, crn=2222, semester=semester)
        edclasssemester = Assignment.objects.create(edclass=edclass1)#, keyrubric=rubric)
        edclasssemester.keyrubric.add(rubric)
        #semester.classes.add(edclass1)

        response = self.client.get('/assessment/'+semester.text+'/')
        self.assertContains(response, 'EG 5000 01')

    def create_two_classes_for_unit_tests(self):
        semester = Semester.objects.get(text="201530")
        rubric = Rubric.objects.create(name="BOB")
        class1 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="5000", teacher=self.test_user, crn=2222, semester=semester)
        class2 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="6000", teacher=self.test_user, crn=3333, semester=semester)
        edclasssemester = Assignment.objects.create(edclass=class1)#, keyrubric=rubric)
        edclasssemester1 = Assignment.objects.create(edclass=class2)#, keyrubric=rubric)
        edclasssemester.keyrubric.add(rubric)
        edclasssemester1.keyrubric.add(rubric)

    def create_two_semesters_for_unit_tests(self):
        Semester.objects.create(text="201530")
        Semester.objects.create(text="201610")

    def test_displays_two_classes(self):
        self.create_two_semesters_for_unit_tests()
        self.create_two_classes_for_unit_tests()
        semester = Semester.objects.get(text="201530")
        response = self.client.get('/assessment/'+ semester.text +'/')
        self.assertContains(response, "EG 6000 01")
        self.assertContains(response, "EG 5000 01")

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
        edClass = EdClasses.objects.get(subject="EG", coursenumber="5000", teacher=self.test_user)
        request.POST['edClass'] = edClass.subject + edClass.coursenumber

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
        edClass = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="5000", teacher=self.test_user, crn=2222, semester=first_semester)
        edClass2 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="6000", teacher=self.test_user, crn=3333, semester=first_semester)
        edClass1 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="5111", teacher=jane, crn=4444, semester=first_semester)

        #first_semester.classes.add(edClass)
        #first_semester.classes.add(edClass2)
        #first_semester.classes.add(edClass1)
        rubric = Rubric.objects.create(name="bob")
        edclasssemester = Assignment.objects.create(edclass=edClass, assignmentname="Writing Assignment")#, semester=first_semester)#, keyrubric=rubric)
        edclasssemester1 = Assignment.objects.create(edclass=edClass2)#, semester=first_semester)#, keyrubric=rubric)
        edclasssemester2 = Assignment.objects.create(edclass=edClass1)#, semester=first_semester)#, keyrubric=rubric)

        edclasssemester.keyrubric.add(rubric)
        edclasssemester1.keyrubric.add(rubric)
        edclasssemester2.keyrubric.add(rubric)

        bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
        jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")
        kelly = Student.objects.create(lastname="Smith", firstname="Kelly", lnumber="33333333")

        bobenrollment = Enrollment.objects.create(student=bob, edclass=edClass)#, semester=first_semester)
        janeenrollment = Enrollment.objects.create(student=jane,edclass=edClass)#, semester=first_semester), semester=first_semester)
        bobenrollment2 = Enrollment.objects.create(student=bob,edclass=edClass2)#, semester=first_semester), semester=first_semester)
        janeenrollment2 = Enrollment.objects.create(student=jane,edclass=edClass2)#, semester=first_semester), semester=first_semester)
        kellyenrollment = Enrollment.objects.create(student=kelly, edclass=edClass1)#, semester=first_semester), semester=first_semester)


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
        response = self.client.get('/assessment/201530/EG5111/writingassignment1/')
        self.assertNotIn("Smith", response.content.decode())

    def test_jane_class_results_in_404(self):
        #bob is logged in right now.  shouldnt see jane class
        self.add_two_classes_to_semester_add_two_students_to_class()
        response = self.client.get('/assessment/201530/EG5111/writingassignment/1')
        self.assertEqual(response.status_code, 404)

    def test_semester_page_requires_login(self):
        #follow=True follows the redirect to the login page
        response = self.client.get("/assessment/201530/", follow=True)
        self.assertIn("Username", response.content.decode())

    def test_student_page_returns_correct_template(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        response = self.client.get("/assessment/201530/EG500001/writingassignment1/")
        self.assertTemplateUsed(response, 'rubricapp/student.html')

    def test_semester_page_redirects_to_class_url(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        request = HttpRequest()
        Bob = User.objects.get(username='bob')
        request.user = Bob
        request.method = "POST"
        edClass = EdClasses.objects.get(subject="EG", coursenumber="5000", sectionnumber="01")
        request.POST['edClass'] = edClass.subject + edClass.coursenumber + edClass.sectionnumber

        response = semester_page(request, "201530")

        self.assertEqual(response['location'], 'EG500001/')

    def test_semester_page_can_show_without_redirecting(self):
        #TODO setup semester/class/ url
        self.add_two_classes_to_semester_add_two_students_to_class()
        assignmentname = Assignment.objects.get(assignmentname="Writing Assignment")
        response = self.client.get("/assessment/201530/EG500001/writingassignment{}/".format(assignmentname.pk))
        self.assertContains(response, 'Bob DaBuilder')

    def test_class_page_can_take_post_request(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        request = HttpRequest()
        request.method = "POST"
        Bob = User.objects.get(username='bob')
        request.user = Bob
        bob = Student.objects.get(lnumber="21743148")
        request.POST['studentnames'] = bob.lnumber
        assignment= Assignment.objects.get(assignmentname="Writing Assignment")

        response = student_page(request, "EG500001", "201530", "Writing Assignment{}".format(assignment.pk))

        self.assertEqual(response.status_code, 302)

    def test_class_page_redirects_to_student_url(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        request = HttpRequest()
        request.method = 'POST'
        Bob = User.objects.get(username='bob')
        request.user = Bob
        student = Student.objects.get(lnumber="21743148")
        request.POST['studentnames'] = student.lnumber
        assignment = Assignment.objects.get(assignmentname="Writing Assignment")

        response = student_page(request, "EG500001", "201530", "Writing Assignment{}".format(assignment.pk))

        self.assertEqual(response.status_code, 302)

        self.assertEqual(response['location'], '21743148/')

    def test_class_page_shows_url_if_no_students(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        bobenrollment = Enrollment.objects.get(student__lastname="DaBuilder", edclass__subject="EG", edclass__coursenumber="5000")
        edclass= EdClasses.objects.get(crn=2222)
        assignment = Assignment.objects.get(assignmentname="Writing Assignment", edclass=edclass)
        bobrubric = RubricData.objects.get_or_create(assignment=assignment, enrollment=bobenrollment)
        bobrubric[0].rubriccompleted = True
        bobrubric[0].save()

        janeenrollment = Enrollment.objects.get(student__lastname="Doe", edclass__subject="EG", edclass__coursenumber="5000")
        janerubric = RubricData.objects.get_or_create(assignment=assignment, enrollment=janeenrollment)
        janerubric[0].rubriccompleted = True
        janerubric[0].save()

        response = self.client.get("/assessment/201530/EG500001/writingassignment1/")
        print(response.content.decode())
        self.assertIn("Return to the semester page", response.content.decode())

    def test_class_page_does_not_show_students_from_other_semesters(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        booritter = Student.objects.create(lastname="Ritter", firstname="Elaine", lnumber="21743142")
        newsemester = Semester.objects.create(text="201610")
        bob = User.objects.create(username="Bob")
        edclass = EdClasses.objects.create(crn=7777, subject="EG", coursenumber="5001", semester=newsemester, teacher=bob)
        #newsemester.classes.add(edclass)
        edclassenrollment = Assignment.objects.create(edclass=edclass)
        booenrollment = Enrollment.objects.create(student=booritter, edclass=edclass)#, semester=newsemester)
        response = self.client.get('/assessment/201530/EG500001/writingassignment1/')
        self.assertNotContains(response, "Elaine")

class AssignmentViewTest(TestCase):

    def add_two_classes_to_semester_add_two_students_to_class(self):
        self.client = Client()
        self.username = 'bob'
        self.email = 'test@test.com'
        self.password = 'test'
        self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
        login = self.client.login(username=self.username, password = self.password)
        jane = User.objects.create(username="Jane")


        first_semester = Semester.objects.create(text='201530')
        edClass = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="5000", teacher=self.test_user, crn=2222, semester=first_semester)
        edClass2 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="6000", teacher=self.test_user, crn=3333, semester=first_semester)
        edClass1 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="5111", teacher=jane, crn=4444, semester=first_semester)

        #first_semester.classes.add(edClass)
        #first_semester.classes.add(edClass2)
        #first_semester.classes.add(edClass1)
        writingrubric = Rubric.objects.create(name="Writing Rubric")
        unitrubric = Rubric.objects.create(name="Unit Rubric")
        unitassignment = Assignment.objects.create(edclass=edClass, assignmentname="Unit Plan")
        writingassignment = Assignment.objects.create(edclass=edClass, assignmentname="Writing Assignment")
        edclasssemester1 = Assignment.objects.create(edclass=edClass2)
        edclasssemester2 = Assignment.objects.create(edclass=edClass1)

        unitassignment.keyrubric.add(unitrubric)
        writingassignment.keyrubric.add(writingrubric)
        edclasssemester1.keyrubric.add(unitrubric)
        edclasssemester2.keyrubric.add(unitrubric)

        row1 = Row.objects.create(excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)

        row2 = Row.objects.create(excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)

        row1 = Row.objects.create(excellenttext="BAD!",
                                  proficienttext="BAD!",
                                  satisfactorytext="BAD!",
                                  unsatisfactorytext="BAD!",rubric=unitrubric)

        row2 = Row.objects.create(excellenttext="BAD!",
                                  proficienttext="BAD!",
                                  satisfactorytext="BAD!",
                                  unsatisfactorytext="BAD!",rubric=unitrubric)


        bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
        jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")
        kelly = Student.objects.create(lastname="Smith", firstname="Kelly", lnumber="33333333")

        bobenrollment = Enrollment.objects.create(student=bob, edclass=edClass)#, semester=first_semester)
        janeenrollment = Enrollment.objects.create(student=jane,edclass=edClass)#, semester=first_semester), semester=first_semester)
        bobenrollment2 = Enrollment.objects.create(student=bob,edclass=edClass2)#, semester=first_semester), semester=first_semester)
        janeenrollment2 = Enrollment.objects.create(student=jane,edclass=edClass2)#, semester=first_semester)
        kellyenrollment = Enrollment.objects.create(student=kelly, edclass=edClass1)#, semester=first_semester)



    def test_assignment_page_resolves_to_assingment_function(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        found = resolve('/assessment/201530/EG500001/writingassignment1/')
        self.assertEqual(found.func, student_page)

    def test_student_can_have_more_than_one_assignment_in_course(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        edclass = EdClasses.objects.get(crn=2222)
        writingassignment = Assignment.objects.get(assignmentname="Writing Assignment")
        unitassignment = Assignment.objects.get(assignmentname="Unit Plan")
        data ={"form-TOTAL_FORMS": "2",
               "form-INITIAL_FORMS": "2",
               "form-MIN_NUM_FORMS": "0",
               "form-MAX_NUM_FORMS": "1000",
               "form-0-row_choice":"2",
               "form-1-row_choice":"2",
               "form-0-id": "3",
               "form-1-id": "4"}

        response = self.client.post("/assessment/201530/EG500001/writingassignment{}/21743148/".format(writingassignment.pk), data)
        found = self.client.get('/assessment/201530/EG500001/unitplan{}/21743148/'.format(unitassignment.pk))
        self.assertContains(found, "BAD!")



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
        edclass1 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="5000", teacher=self.test_user, crn=2222, semester=semester)
        edclass2 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="6000",  teacher=self.test_user, crn=3333, semester=semester)
        edclass = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="5111", teacher=jane, crn=4444, semester=semester)
        #semester.classes.add(edclass1)
        #semester.classes.add(edclass2)
        #semester.classes.add(edclass)

        bob = Student.objects.create(lastname="DaBuilder", firstname="Bob",lnumber="21743148")
        jane = Student.objects.create(lastname="Doe", firstname="Jane",lnumber="21743149")
        kelly = Student.objects.create(lastname="Smith", firstname="Kelly", lnumber="33333333")

        kellyenrollment = Enrollment.objects.create(student=kelly, edclass=edclass)#, semester=semester)
        bobenrollment = Enrollment.objects.create(student=bob, edclass=edclass1)#, semester=semester), semester=semester)
        bobenrollment1 = Enrollment.objects.create(student=bob, edclass=edclass2)#, semester=semester), semester=semester)
        janeenrollment = Enrollment.objects.create(student=jane, edclass=edclass1)#, semester=semester), semester=semester)
        janeenrollment2 = Enrollment.objects.create(student=jane, edclass=edclass2)#, semester=semester), semester=semester)
        writingrubric = Rubric.objects.create(name="writingrubric")

        row1 = Row.objects.create(excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)

        row2 = Row.objects.create(excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)



        edclasssemester = Assignment.objects.create( edclass=edclass, assignmentname="Writing Assignment")#, keyrubric=writingrubric)
        edclasssemester1 = Assignment.objects.create( edclass=edclass1, assignmentname="Writing Assignment")#, keyrubric=writingrubric)
        edclasssemester2 = Assignment.objects.create(edclass=edclass2, assignmentname="Writing Assignment")#, keyrubric=writingrubric)
        edclasssemester.keyrubric.add(writingrubric)
        edclasssemester1.keyrubric.add(writingrubric)
        edclasssemester2.keyrubric.add(writingrubric)


        #Many to many relationship must be added after creation of objects
        #because the manyto-many relationship is not a column in the database
        #edclass1.keyrubric.add(writingrubric)
        #edclass2.keyrubric.add(writingrubric)
        #edclass.keyrubric.add(writingrubric)


    def test_rubric_page_not_viewable_by_dasterdaly_bob(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
        response = self.client.get('/assessment/201530/EG5111/writingassignment1/33333333/')
        self.assertEquals(response.status_code, 404)

    def test_class_page_requires_login(self):
        response = self.client.get("/assessment/201530/EG500001", follow=True)
        self.assertIn("Username", response.content.decode())

    def test_student_and_rubric_view_returns_correct_template(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
        response = self.client.get("/assessment/201530/EG500001/writingassignment1/21743148/")
        self.assertTemplateUsed(response, 'rubricapp/rubric.html')

    def test_student_and_rubric_view_shows_student_name(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
        response = self.client.get("/assessment/201530/EG500001/writingassignment1/21743148/")
        self.assertContains(response, "DaBuilder, Bob")

    def test_student_and_rubric_view_has_excellent_grade(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
        response = self.client.get("/assessment/201530/EG500001/writingassignment1/21743148/")
        self.assertContains(response, "Excellent")

    def test_rubric_shows_a_cell_under_excellent(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
        response = self.client.get("/assessment/201530/EG500001/writingassignment1/21743148/")
        self.assertContains(response, "THE BEST!")

    def test_rubric_page_shows_rubric_name(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
        response = self.client.get("/assessment/201530/EG500001/writingassignment1/21743148/")
        self.assertContains(response, "Writing Rubric")

    def test_rubric_page_can_take_post_request(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()

        response = self.client.get("/assessment/201530/EG500001/writingassignment1/21743148/")
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
        response = self.client.post("/assessment/201530/EG500001/writingassignment1/21743148/", data)

        self.assertEqual(response.status_code, 302)

    def test_post_request_creates_new_rubric_for_the_enrollment(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()

        writingrubric = Rubric.objects.get(name="writingrubric")

        row = Row.objects.filter(rubric=writingrubric)
        self.assertEqual(row.count(), 2)
        #Why do you need to get the response before you can post it?????
        response = self.client.get("/assessment/201530/EG500001/writingassignment1/21743148/")
        data ={"form-TOTAL_FORMS": "2",
               "form-INITIAL_FORMS": "2",
               "form-MIN_NUM_FORMS": "0",
               "form-MAX_NUM_FORMS": "1000",
               "form-0-row_choice":"1",
               "form-1-row_choice":"2",
               "form-0-id": "3",
               "form-1-id": "4"}

        response = self.client.post("/assessment/201530/EG500001/writingassignment1/21743148/", data)
        student = Student.objects.get(lnumber="21743148")
        edclass = EdClasses.objects.get(subject="EG", coursenumber="5000", sectionnumber="01")
        writingassignment = Assignment.objects.get(pk=1)
        bobenroll = Enrollment.objects.get(edclass=edclass, student=student)
        bobrubricobject = RubricData.objects.get(assignment=writingassignment, enrollment=bobenroll)

        self.assertEqual(bobrubricobject.completedrubric.name, "EG50000121743148201530WritingAssignment")

    def test_rubric_page_redirects_correct_page(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()

        response = self.client.get("/assessment/201530/EG500001/writingassignment1/21743148/")
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
        response = self.client.post("/assessment/201530/EG500001/writingassignment1/21743148/", data)

        self.assertEqual(response['location'], 'http://testserver/assessment/201530/EG500001/writingassignment1/')

    def test_post_request_updates_correct_model(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()

        #Why do you need to get the response before you can post it?????
        response = self.client.get("/assessment/201530/EG500001/writingassignment1/21743148/")
        data ={"form-TOTAL_FORMS": "2",
               "form-INITIAL_FORMS": "2",
               "form-MIN_NUM_FORMS": "0",
               "form-MAX_NUM_FORMS": "1000",
               "form-0-row_choice":"1",
               "form-1-row_choice":"2",
               "form-0-id": "3",
               "form-1-id": "4"}

        response = self.client.post("/assessment/201530/EG500001/writingassignment1/21743148/", data)
        student = Student.objects.get(lnumber="21743148")
        edclass = EdClasses.objects.get(subject="EG", coursenumber="5000")

        bobenrollment = Enrollment.objects.get(student=student, edclass=edclass)
        bobrubricenroll = RubricData.objects.get(assignment__pk=1, enrollment=bobenrollment)
        row = Row.objects.get(excellenttext="THE BEST!", rubric__name=bobrubricenroll.completedrubric.name)
        self.assertEqual(row.row_choice, "1")

    def test_post_request_does_not_take_0_value(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
        response = self.client.get("/assessment/201530/EG500001/writingassignment1/21743148/")
        data ={"form-TOTAL_FORMS": "2",
               "form-INITIAL_FORMS": "2",
               "form-MIN_NUM_FORMS": "0",
               "form-MAX_NUM_FORMS": "1000",
               "form-0-row_choice":"0",
               "form-1-row_choice":"2",
               "form-0-id": "3",
               "form-1-id": "4"}


        response = self.client.post("/assessment/201530/EG500001/writingassignment1/21743148/", data)
        self.assertContains(response, "You must choose a value for all rows!" )

    def test_post_request_with_0_value_doesnt_return_null_row_values(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
        response = self.client.get("/assessment/201530/EG500001/writingassignment1/21743148/")
        data ={"form-TOTAL_FORMS": "2",
               "form-INITIAL_FORMS": "2",
               "form-MIN_NUM_FORMS": "0",
               "form-MAX_NUM_FORMS": "1000",
               "form-0-row_choice":"0",
               "form-1-row_choice":"2",
               "form-0-id": "3",
               "form-1-id": "4"}


        response = self.client.post("/assessment/201530/EG500001/writingassignment1/21743148/", data)
        self.assertContains(response, "THE BEST!" )

    def test_post_request_does_not_create_blank_enrollment_if_empty_row(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
        response = self.client.get("/assessment/201530/EG500001/writingassignment1/21743148/")
        data ={"form-TOTAL_FORMS": "2",
               "form-INITIAL_FORMS": "2",
               "form-MIN_NUM_FORMS": "0",
               "form-MAX_NUM_FORMS": "1000",
               "form-0-row_choice":"0",
               "form-1-row_choice":"2",
               "form-0-id": "3",
               "form-1-id": "4"}


        response = self.client.post("/assessment/201530/EG500001/writingassignment1/21743148/", data)
        student = Student.objects.get(lnumber="21743148")
        edclass = EdClasses.objects.get(subject="EG", coursenumber="5000")

        bobenrollment = Enrollment.objects.filter(student=student, edclass=edclass)
        self.assertEqual(bobenrollment.count(), 1)

    def test_get_request_for_student_rubric_page_returns_rubric_if_completedrubric_false(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
        bobenrollment = Enrollment.objects.get(student__lastname="DaBuilder", edclass__subject="EG", edclass__coursenumber="5000")
        Rubric.objects.create(name="EG50000121743148201530")
        bobenrollment.rubriccompleted = False
        response = self.client.get("/assessment/201530/EG500001/WritingAssignment1/21743148/")
        self.assertContains(response, "id_form-TOTAL_FORMS")

    def test_rubric_for_different_semester_doesnt_shows_up_in_correct_semester(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
        newsemester = Semester.objects.create(text="201610")
        bob = User.objects.get(username="bob")
        badrubric = Rubric.objects.create()
        badrow = Row.objects.create(excellenttext="STOP",
                                    proficienttext="STOP",
                                    satisfactorytext="STOP",
                                    unsatisfactorytext="STOP",rubric=badrubric)

        edclass = EdClasses.objects.create(subject="EG", sectionnumber="01", coursenumber="5000", crn=7777, teacher=bob, semester=newsemester)#, semester=newsemester)
        edclassnewsemester = Assignment.objects.create(edclass=edclass, assignmentname="Writing Assignment")
        edclassnewsemester.keyrubric.add(badrubric)
        george = Student.objects.create(lastname="Harrison", firstname="Georgeo", lnumber="21743444")
        newgeorgeenrollment = Enrollment.objects.create(student=george, edclass=edclass)#,semester=newsemester)
        response = self.client.get('/assessment/201610/EG500001/WritingAssignment'+ str(edclassnewsemester.pk) +'/21743444/')
        self.assertContains(response, "STOP")

    def test_rubric_for_different_semester_doesnt_show_up_wrong_semester(self):
        self.add_two_classes_to_semester_add_two_students_to_class_add_one_row()
        newsemester = Semester.objects.create(text="201610")
        badrubric = Rubric.objects.create()
        badrow = Row.objects.create(excellenttext="STOP",
                                    proficienttext="STOP",
                                    satisfactorytext="STOP",
                                    unsatisfactorytext="STOP",rubric=badrubric)

        edclass = EdClasses.objects.get(subject="EG", coursenumber="5000")#Should be in 201530
        edclassnewsemester = Assignment.objects.create(edclass=edclass)
        edclassnewsemester.keyrubric.add(badrubric)
        george = Student.objects.create(lastname="Harrison", firstname="Georgeo", lnumber="5555")
        newgeorgeenrollment = Enrollment.objects.create(student=george, edclass=edclass)#,semester=newsemester)
        response = self.client.get('/assessment/201530/EG500001/writingassignment1/21743148/')
        self.assertNotContains(response, "STOP")



class UserLoginTest(TestCase):

    def test_login_page_exists(self):
        response  = self.client.get('/assessment/201530/')
        self.assertEqual(response.status_code, 302)

    def test_login_page_takes_name(self):
        response = self.client.get('/login/')
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_change_password_page_works(self):
        self.client = Client()
        self.username = 'bob'
        self.email = 'test@test.com'
        self.password = 'test'
        self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
        login = self.client.login(username=self.username, password = self.password)
        response = self.client.get('/password_change/')
        self.assertContains(response, 'password')

class UserPageTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.username = 'bob'
        self.email = 'test@test.com'
        self.password = 'bob'
        self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
        login = self.client.login(username=self.username, password=self.password)

    def test_user_view_exists(self):
        request = HttpRequest()
        Bob = User.objects.get(username='bob')
        request.user = Bob
        response =  user_page(request)
        self.assertContains(response, 'Change Password')

    def test_user_page_exists(self):
        response = self.client.get('/user/')
        self.assertEquals(response.status_code, 200)

    def test_user_page_requires_login(self):
        self.client.logout()
        response = self.client.get('/user/')
        self.assertRedirects(response, '/login/?next=/user/', status_code=302)

    def test_user_page_shows_correct_links(self):
        response = self.client.get('/user/')
        self.assertContains(response, "Reset Password")
        self.assertContains(response, "Logout")





