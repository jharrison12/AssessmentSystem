from unittest import skip
from rubricapp.models import Semester, EdClasses, Student, Enrollment, Rubric, Row, Assignment, RubricData, Standard
from django.template.loader import render_to_string
from django.http import HttpRequest
from django.test import TestCase
from rubricapp.views import home_page, semester_page, student_page, rubric_page
from django.db import IntegrityError
from django.contrib.auth.models import User

class RubricModel(TestCase):

    def create_rubric_and_rows_connect_to_class(self):
        bob = User.objects.create(username="Bob")
        semester = Semester.objects.create(text="201530")
        edclass1 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="5000",  teacher=bob, crn=2222,semester=semester)
        edclass2 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="6000", teacher=bob, crn=3333, semester=semester)
        #semester.classes.add(edclass1)
        #semester.classes.add(edclass2)
        #edclasssemester1 = Assignment.objects.create(edclass=edclass1, keyrubric=writingrubric)
        #edclasssemester2 = Assignment.objects.create(edclass=edclass2, keyrubric=writingrubric)

        bob = Student.objects.create(lastname="DaBuilder", firstname="Bob",lnumber="21743148")
        jane = Student.objects.create(lastname="Doe", firstname="Jane",lnumber="21743149")

        bobenrollment = Enrollment.objects.create(student=bob, edclass=edclass1)#, semester=semester)
        bobenrollment1 = Enrollment.objects.create(student=bob, edclass=edclass2)#, semester=semester), semester=semester)
        janeenrollment = Enrollment.objects.create(student=jane, edclass=edclass1)#, semester=semester), semester=semester)
        janeenrollment2 = Enrollment.objects.create(student=jane, edclass=edclass2)#, semester=semester), semester=semester)
        writingrubric = Rubric.objects.create(name="writingrubric")
        edclasssemester1 = Assignment.objects.create(edclass=edclass1, keyrubric=writingrubric)
        edclasssemester2 = Assignment.objects.create(edclass=edclass2, keyrubric=writingrubric)

        row1 = Row.objects.create(excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)

        #Many to many relationship must be added after creation of objects
        #because the manyto-many relationship is not a column in the database
        #edclasssemester1.keyrubric.add(writingrubric)
        #edclasssemester2.keyrubric.add(writingrubric)

    def test_rubric_connected_with_enrollment_class(self):
        self.create_rubric_and_rows_connect_to_class()
        rubrics = Rubric.objects.all()
        self.assertEqual(rubrics.count(), 1)

    def test_to_make_sure_class_object_matches_with_rubric(self):
        self.create_rubric_and_rows_connect_to_class()
        bob = Student.objects.get(lnumber="21743148")
        edClass = EdClasses.objects.get(sectionnumber="01",subject='EG', coursenumber='5000')#, semester="201530")
        edclasssemesterobj = Assignment.objects.get(edclass=edClass)
        #should get the only rubric attached to the object
        writingrubric = edclasssemesterobj.keyrubric
        self.assertEqual(writingrubric.name, "writingrubric")

    def test_rubric_object_only_has_one_row(self):
        self.create_rubric_and_rows_connect_to_class()
        writingrubric = Rubric.objects.get(name="writingrubric")
        rows = Row.objects.filter(rubric=writingrubric)
        self.assertEqual(rows.count(), 1)

    def test_rubric_object_connects_with_multiple_rows(self):
        #This test is more for the developer than the application.
        self.create_rubric_and_rows_connect_to_class()
        writingrubric = Rubric.objects.get(name="writingrubric")
        row2 = Row.objects.create(excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)
        rows = Row.objects.filter(rubric=writingrubric)
        self.assertEqual(rows.count(), 2)

    def test_query_to_pull_rubric_and_check_text(self):
        #Check that row object can be filtered based upon text
        self.create_rubric_and_rows_connect_to_class()
        writingrubric = Rubric.objects.get(name="writingrubric")
        row2 = Row.objects.create(excellenttext="THE GREATEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)
        rows = Row.objects.get(excellenttext="THE GREATEST!")
        self.assertIn(rows.proficienttext, "THE SECOND BEST!")

    def test_jane_rubric_and_bob_rubric_are_different(self):
        self.create_rubric_and_rows_connect_to_class()
        jane = Student.objects.get(lnumber="21743149")
        bob = Student.objects.get(lnumber="21743148")
        edClass = EdClasses.objects.get(subject="EG", coursenumber="5000", semester__text="201530")
        blankrubic = Rubric.objects.create(name="NOt a rubric")
        writingrubric = Rubric.objects.create(name="writingrubric2")
        writingrubric1 = Rubric.objects.create(name="writingrubric1")
        newassignment = Assignment.objects.create(assignmentname="New Assignment", edclass=edClass, keyrubric=blankrubic)
        bobenrollment = Enrollment.objects.get(student=bob, edclass=edClass)
        janeenrollment = Enrollment.objects.get(student=jane, edclass=edClass)
        bobrubricdata = RubricData.objects.create(assignment=newassignment, enrollment=bobenrollment,completedrubric=writingrubric)
        janerubricdata = RubricData.objects.create(assignment=newassignment, enrollment=janeenrollment,completedrubric=writingrubric1)

        janerubric = Rubric.objects.get(rubricdata__enrollment__student=jane)
        bobrubric = Rubric.objects.get(rubricdata__enrollment__student=bob)

        self.assertNotEqual(bobrubric, janerubric)
    #TODO fix this
    @skip
    def test_duplicate_rubric_objects_are_invalid(self):
        self.create_rubric_and_rows_connect_to_class()
        rubric = Rubric.objects.create(name="writingrubric")
        with self.assertRaises(ValidationError):
            rubric = Rubric(name="writingrubric")
            rubric.full_clean()

class ClassAndSemesterModelTest(TestCase):

    def create_rubric_and_rows_connect_to_class(self):
        bob = User.objects.create(username="Bob")
        semester = Semester.objects.create(text="201530")
        edclass1 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="5000", teacher=bob, crn=2222,semester=semester)
        edclass2 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="6000", teacher=bob, crn=3333, semester=semester)
        #semester.classes.add(edclass1)
        #semester.classes.add(edclass2)




        bob = Student.objects.create(lastname="DaBuilder", firstname="Bob",lnumber="21743148")
        jane = Student.objects.create(lastname="Doe", firstname="Jane",lnumber="21743149")

        bobenrollment = Enrollment.objects.create(student=bob, edclass=edclass1)#, semester=semester)
        bobenrollment1 = Enrollment.objects.create(student=bob, edclass=edclass2)#, semester=semester), semester=semester)
        janeenrollment = Enrollment.objects.create(student=jane, edclass=edclass1)#, semester=semester), semester=semester)
        janeenrollment2 = Enrollment.objects.create(student=jane, edclass=edclass2)#, semester=semester), semester=semester)
        writingrubric = Rubric.objects.create(name="writingrubric")

        edclasssemester1 = Assignment.objects.create(edclass=edclass1, keyrubric=writingrubric)
        edclasssemester2 = Assignment.objects.create(edclass=edclass2, keyrubric=writingrubric)#, semester=semester)

        row1 = Row.objects.create(excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)

        #Many to many relationship must be added after creation of objects
        #because the manyto-many relationship is not a column in the database
        #edclasssemester1.keyrubric.add(writingrubric)

    def test_class_model_identifier_is_crn(self):
        self.create_rubric_and_rows_connect_to_class()
        bob = User.objects.get(username="Bob")
        semester = Semester.objects.get(text="201530")
        edclass2 = EdClasses.objects.create(subject="EG", coursenumber="5000", crn=30140, teacher=bob, semester=semester)
        edclass1 = EdClasses.objects.get(subject="EG", coursenumber="5000", crn=2222)
        self.assertNotEqual(edclass1, edclass2)

class EnrollmentModelTest(TestCase):

    def add_two_classes_to_semester_add_two_students_to_class(self):
        first_semester = Semester.objects.create(text='201530')
        bob = User.objects.create(username="Bob")
        janeteacher = User.objects.create(username="Jane")
        edClass = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="5000", teacher=bob, crn=2222, semester=first_semester)
        edClass2 = EdClasses.objects.create(sectionnumber="01",subject="EG", coursenumber="6000", teacher=bob, crn=3333, semester=first_semester)
        keyrubric = Rubric.objects.create(name="Blank Rubric")
        edclasssemester1 = Assignment.objects.create(edclass=edClass, keyrubric=keyrubric)
        edclasssemester2 = Assignment.objects.create(edclass=edClass2, keyrubric=keyrubric)
        #first_semester.classes.add(edClass)
        #first_semester.classes.add(edClass2)


        bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
        jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")

        bobenrollment = Enrollment.objects.create(student=bob, edclass=edClass)#, semester=first_semester)
        janeenrollment = Enrollment.objects.create(student=jane,edclass=edClass)#, semester=first_semester), semester=first_semester)
        bobenrollment2 = Enrollment.objects.create(student=bob,edclass=edClass2)#, semester=first_semester), semester=first_semester)
        janeenrollment2 = Enrollment.objects.create(student=jane,edclass=edClass2)#, semester=first_semester),  semester=first_semester)


    def test_class_connect_to_particular_user(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        bob = User.objects.get(username="Bob")
        edclass = EdClasses.objects.get(subject="EG", coursenumber="5000")
        self.assertEqual(edclass.teacher, bob)

    def test_different_teacher_does_not_connect_to_bob_class(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        jane = User.objects.get(username="Jane")
        edclass = EdClasses.objects.get(subject="EG", coursenumber="5000")
        self.assertNotEqual(edclass.teacher, jane)


    def test_model_for_semesters(self):
        first_semester = Semester()
        first_semester.text = '201530'
        first_semester.save()

        second_semester = Semester()
        second_semester.text = '201610'
        second_semester.save()

        saved_items = Semester.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_semester = saved_items[0]
        second_saved_semester = saved_items[1]
        self.assertEqual(first_saved_semester.text, '201530')
        self.assertEqual(second_saved_semester.text, '201610')

    def test_model_for_classes(self):
        self.add_two_classes_to_semester_add_two_students_to_class()

        saved_classes = EdClasses.objects.all()
        self.assertEqual(saved_classes.count(), 2)

        first_saved_class = saved_classes[0]
        second_saved_class = saved_classes[1]

        self.assertEqual(first_saved_class.subject + " " + first_saved_class.coursenumber, 'EG 5000')
        self.assertEqual(second_saved_class.subject + " " + second_saved_class.coursenumber, 'EG 6000')

    def test_classes_link_to_semester(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        #first_semester = Semester.objects.get(text='201530')


        saved_classes = EdClasses.objects.all()
        first_saved_class = saved_classes[0]
        second_saved_class = saved_classes[1]
        edclasssemester1 = Assignment.objects.get(edclass__subject="EG", edclass__coursenumber="5000")
        edclasssemester2  =Assignment.objects.get(edclass__subject="EG", edclass__coursenumber="6000")

        self.assertEqual(edclasssemester1.edclass ,first_saved_class )
        self.assertEqual(edclasssemester2.edclass, second_saved_class )

    def test_students_link_to_class(self):
        self.add_two_classes_to_semester_add_two_students_to_class()

        oneclass = EdClasses.objects.get(subject="EG", coursenumber="5000")
        twoclass = EdClasses.objects.get(subject="EG", coursenumber="6000")

        jane = Student.objects.get(lnumber="21743149")
        bob = Student.objects.get(lnumber="21743148")

        self.assertQuerysetEqual(oneclass.students.filter(lnumber="21743149"), [jane])
        self.assertQuerysetEqual(twoclass.students.filter(lnumber="21743148"), [bob])

    def test_enrollment_model_creates_correct_number_of_enrollments(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        enrollments = Enrollment.objects.all()

        self.assertEqual(enrollments.count(),4)

    def test_students_link_to_enrollments(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        edclass1 = EdClasses.objects.get(subject="EG", coursenumber="5000")
        bob = Student.objects.get(lnumber="21743148")
        rubric = Rubric.objects.get(name="Blank Rubric")
        writing = Assignment.objects.create(assignmentname="Writing Assignment", edclass=edclass1, keyrubric=rubric)
        bobenrollment = Enrollment.objects.get(edclass=edclass1, student=bob)
        bobenrollmentrubric = RubricData.objects.create(enrollment=bobenrollment, assignment=writing)
        self.assertEqual(bobenrollmentrubric.rubriccompleted, False)

    def test_students_are_pulled_by_class_and_semester(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        second_semester = Semester.objects.create(text="201610")
        bob = User.objects.get(username="Bob")
        edClass = EdClasses.objects.create(subject="EG", coursenumber="5000", crn=55555, semester=second_semester, teacher=bob)
        #edclasssemester.objects.create()
        studentsinclass = Student.objects.filter(edclasses=edClass)#, enrollment__semester=second_semester)
        self.assertEqual(studentsinclass.count(), 0)

    def test_students_can_be_added_to_class_by_semester(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        bob = User.objects.get(username="Bob")
        second_semester = Semester.objects.create(text="201610")
        edclass = EdClasses.objects.create(subject="EG", coursenumber="5000",semester=second_semester, teacher=bob, crn=7777)
        #second_semester.classes.add(edclass)
        elaine = Student.objects.create(lastname="Ritter", firstname="Elaine", lnumber="21743142")
        elainenrollment = Enrollment.objects.create(student=elaine, edclass=edclass)#, semester=second_semester)
        studentsinclass = Student.objects.filter(edclasses=edclass)#, enrollment__semester=second_semester)
        self.assertEqual(studentsinclass.count(), 1)

    def test_students_are_not_enrolled_in_same_course_in_different_semesters(self):
        self.add_two_classes_to_semester_add_two_students_to_class()
        second_semester = Semester.objects.create(text="201610")
        edclass = EdClasses.objects.get(subject="EG", coursenumber="5000")
        #second_semester.classes.add(edclass)
        elaine = Student.objects.create(lastname="Ritter", firstname="Elaine", lnumber="21743142")
        #elainenrollment = Enrollment.objects.create(student=elaine, edclass=edclass)#, semester=second_semester)
        first_semester = Semester.objects.get(text='201530')
        studentsinclass = Student.objects.filter(edclasses=edclass)#, enrollment__semester=first_semester)
        self.assertNotIn("21743142", [i for i in studentsinclass])

class StandardsTest(TestCase):

    def create_rubric_and_row(self):
        writingrubric = Rubric.objects.create(name="writingrubric")
        row1 = Row.objects.create(name="ROW 1",
                                  excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)

    def test_standard_aligns_to_rubric(self):
        self.create_rubric_and_row()
        standard1 = Standard.objects.create(name="INTASC 1.0")
        row1 = Row.objects.get(name="ROW 1")
        row1.standards.add(standard1)
        self.assertEqual(row1.standards.count(),1)

    def test_multi_standard_aligns_to_rubric(self):
        self.create_rubric_and_row()
        standard1 = Standard.objects.create(name="INTASC 1.0")
        standard2 = Standard.objects.create(name="INTASC 2.0")
        row1 = Row.objects.get(name="ROW 1")
        row1.standards.add(standard1)
        row1.standards.add(standard2)
        self.assertEqual(row1.standards.count(),2)

    def test_standards_align_to_more_than_one_rubric(self):
        self.create_rubric_and_row()
        standard1 = Standard.objects.create(name="INTASC 1")
        row1 = Row.objects.get(name="ROW 1")
        row1.standards.add(standard1)

        unitrubric = Rubric.objects.create(name="Unit Rubric")
        row2 = Row.objects.create(name="ROW 2",
                                  excellenttext="THE BEST!",
                                  proficienttext="THE SECOND BEST!",
                                  satisfactorytext="THE THIRD BEST!",
                                  unsatisfactorytext="YOU'RE LAST",rubric=unitrubric)

        row2.standards.add(standard1)
        self.assertEqual(Row.objects.filter(standards__name="INTASC 1").count(), 2)

    @unittest.skip
    def test_standards_with_space_enter_in_to_database_without_space(self):
        self.create_rubric_and_row()
        standard1 = Standard.objects.create(name="CAEP R1.4 Professional Responsibility")
        standardcopy = Standard.objects.get(name)

