from unittest import skip
from rubricapp.models import Semester, EdClasses, Student, Enrollment, Rubric, Row
from django.template.loader import render_to_string
from django.http import HttpRequest
from django.test import TestCase
from rubricapp.views import home_page, semester_page, student_page, rubric_page
from django.core.urlresolvers import resolve

class RubricModel(TestCase):
			
	def create_rubric_and_rows_connect_to_class(self):
		semester = Semester.objects.create(text="201530")
		edclass1 = EdClasses.objects.create(name="EG 5000")
		edclass2 = EdClasses.objects.create(name="EG 6000")
		semester.classes.add(edclass1)
		semester.classes.add(edclass2)
		
		bob = Student.objects.create(lastname="DaBuilder", firstname="Bob",lnumber="21743148")
		jane = Student.objects.create(lastname="Doe", firstname="Jane",lnumber="21743149")
		
		bobenrollment = Enrollment.objects.create(student=bob, edclass=edclass1)
		bobenrollment1 = Enrollment.objects.create(student=bob, edclass=edclass2)
		janeenrollment = Enrollment.objects.create(student=jane, edclass=edclass1)
		janeenrollment2 = Enrollment.objects.create(student=jane, edclass=edclass2)
		writingrubric = Rubric.objects.create(name="writingrubric")
		
		row1 = Row.objects.create(excellenttext="THE BEST!", 
								  proficienttext="THE SECOND BEST!",
								  satisfactorytext="THE THIRD BEST!",
								  unsatisfactorytext="YOU'RE LAST",rubric=writingrubric)
							
		#Many to many relationship must be added after creation of objects
		#because the manyto-many relationship is not a column in the database
		edclass1.keyrubric.add(writingrubric)
		edclass1.keyrubric.add(writingrubric)
		
	def test_rubric_connected_with_enrollment_class(self):
		self.create_rubric_and_rows_connect_to_class()
		rubrics = Rubric.objects.all()
		self.assertEqual(rubrics.count(), 1)
		
	def test_to_make_sure_class_object_matches_with_rubric(self):
		self.create_rubric_and_rows_connect_to_class()
		bob = Student.objects.get(lnumber="21743148")
		edClass = EdClasses.objects.get(name='EG 5000')#, semester="201530")
		enrollmentObj = Enrollment.objects.get(student=bob, edclass=edClass)
		#should get the only rubric attached to the object
		writingrubric = edClass.keyrubric.get()
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
		edClass = EdClasses.objects.get(name='EG 5000', semester__text="201530")
		writingrubric = Rubric.objects.create(name="writingrubric2")
		writingrubric1 = Rubric.objects.create(name="writingrubric1")
		bobenrollment = Enrollment.objects.get(student=bob, edclass=edClass)
		janeenrollment = Enrollment.objects.get(student=jane, edclass=edClass)
		bobenrollment.completedrubric = writingrubric
		bobenrollment.save()
		janeenrollment.completedrubric = writingrubric1
		janeenrollment.save()

		janerubric = Rubric.objects.get(enrollment__student=jane)
		bobrubric = Rubric.objects.get(enrollment__student=bob)
		
		self.assertNotEqual(bobrubric, janerubric)
		
class ClassAndSemesterModelTest(TestCase):
	
	def add_two_classes_to_semester_add_two_students_to_class(self):
		first_semester = Semester.objects.create(text='201530')
		edClass = EdClasses.objects.create(name='EG 5000') 
		edClass2 = EdClasses.objects.create(name='EG 6000')
		
		first_semester.classes.add(edClass)
		first_semester.classes.add(edClass2)
		
		
		bob = Student.objects.create(lastname="DaBuilder", firstname="Bob", lnumber="21743148")
		jane = Student.objects.create(lastname="Doe", firstname="Jane", lnumber="21743149")

		bobenrollment = Enrollment.objects.create(student=bob, edclass=edClass)
		janeenrollment = Enrollment.objects.create(student=jane,edclass=edClass)
		bobenrollment2 = Enrollment.objects.create(student=bob,edclass=edClass2)
		janeenrollment2 = Enrollment.objects.create(student=jane,edclass=edClass2)
		
		
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

		self.assertEqual(first_saved_class.name, 'EG 5000')
		self.assertEqual(second_saved_class.name, 'EG 6000')
	
	def test_classes_link_to_semester(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		first_semester = Semester.objects.get(text='201530')
		
		saved_classes = EdClasses.objects.all()
		first_saved_class = saved_classes[0]
		second_saved_class = saved_classes[1]

		self.assertQuerysetEqual(first_semester.classes.filter(name="EG 5000"),[repr(first_saved_class)] )
		self.assertQuerysetEqual(first_semester.classes.filter(name="EG 6000"), [repr(second_saved_class)] )
	
	def test_students_link_to_class(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		
		oneclass = EdClasses.objects.get(name="EG 5000")
		twoclass = EdClasses.objects.get(name="EG 6000")
		
		jane = Student.objects.get(lnumber="21743149")
		bob = Student.objects.get(lnumber="21743148")
		
		self.assertQuerysetEqual(oneclass.students.filter(lnumber="21743149"), [repr(jane)])
		self.assertQuerysetEqual(twoclass.students.filter(lnumber="21743148"), [repr(bob)])
	
	def test_enrollment_model_creates_correct_number_of_enrollments(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		enrollments = Enrollment.objects.all()

		self.assertEqual(enrollments.count(),4)
	
	def test_students_link_to_enrollments(self):
		self.add_two_classes_to_semester_add_two_students_to_class()
		edclass1 = EdClasses.objects.get(name="EG 5000")
		bob = Student.objects.get(lnumber="21743148")
		bobenrollment = Enrollment.objects.get(edclass=edclass1, student=bob)
		self.assertEqual(bobenrollment.rubriccompleted, False)
	

		