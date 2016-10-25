from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

class Student(models.Model):
	firstname = models.TextField(default="")	
	lastname = models.TextField(default="")
	lnumber = models.TextField(default="", unique=True)
	
	def __str__(self):
		return self.lnumber
	#TODO add models


class Rubric(models.Model):
	name = models.TextField(default="Basic Rubric", unique=True)
	template = models.BooleanField(default=True)
	
	def __str__(self):
		return self.name
	
class CompletedRubric(Rubric):
	
	def __str__self(self):
		return self.name
		
class Semester(models.Model):
	text = models.TextField(default='201530')
	#classes = models.ManyToManyField(EdClasses)	
	
	def __str__(self):
		return self.text


class EdClasses(models.Model):
	CHOICES = (
	('EG', "Graduate Education",),
	('EGSE', "Special Education",),
	('EGEL', "English Language Learning"),
	('MAED', 'Math Education'),
	('ED', "Undergraduate Education"),
	)

	crn = models.IntegerField(unique=True, null=False)
	subject = models.CharField(max_length=4, choices=CHOICES, default="EG")
	coursenumber = models.CharField(default='', blank=False, max_length=4)
	sectionnumber = models.CharField(max_length=2, blank=False)
	students = models.ManyToManyField(Student, through="Enrollment")
	#keyrubric = models.ManyToManyField(Rubric)
	semester = models.ManyToManyField(Semester, through="EdClassSemester")
	teacher = models.ForeignKey(User)
	
	def __str__(self):
		return self.subject + " " + self.coursenumber + " " + self.sectionnumber
		

class EdClassSemester(models.Model):
	edclass = models.ForeignKey(EdClasses, null=False)
	semester = models.ForeignKey(Semester, null=False)
	keyrubric = models.ManyToManyField(Rubric)
	
	def __str__(self):
		return "%s %s %s %s" % (self.edclass.subject, self.edclass.coursenumber, self.edclass.sectionnumber, self.semester.text)
	
	class Meta:
		unique_together = ("edclass", "semester")
			
		

class Row(models.Model):
	CHOICES = (
	('0', 'Your string for display'),
	('4','Exemplary'),
	('3','Proficient'),
	('2','Partially Proficient'),
	('1','Incomplete'),
	)
	name = models.CharField(default="None", max_length=30)
	rubric = models.ForeignKey(Rubric)
	row_choice = models.CharField(max_length=20,choices=CHOICES, default="0")
	excellenttext = models.TextField(default="", blank=True)
	proficienttext = models.TextField(default="", blank=True)
	satisfactorytext = models.TextField(default="", blank=True)
	unsatisfactorytext = models.TextField(default="", blank=True)
	
	def __str__(self):
		return self.row_choice

		
class Enrollment(models.Model):
	student = models.ForeignKey(Student, null=False)
	edclass = models.ForeignKey(EdClasses, null=False)
	semester = models.ForeignKey(Semester)
	#Will need to change completedrubric editable to False
	completedrubric = models.OneToOneField(Rubric, null=True, editable=False)
	rubriccompleted = models.BooleanField(default=False)
	
	def encode_class_name_for_admin(self,obj):
		return self.edclass.name + " " + self.semester.text
	
	def __str__(self):
		return 'Enrollment %s: %s' % (self.student, self.edclass)
	
	class Meta:
		unique_together = (("student", "edclass"))
		
	


