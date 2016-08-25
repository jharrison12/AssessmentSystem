from django.db import models
from django.contrib import admin

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

class EdClasses(models.Model):
	name = models.TextField(default='', unique=True)
	students = models.ManyToManyField(Student, through="Enrollment")
	keyrubric = models.ManyToManyField(Rubric)
	def __str__(self):
		return self.name		
		
		
class Semester(models.Model):
	text = models.TextField(default='201530')
	classes = models.ManyToManyField(EdClasses)	
	def __str__(self):
		return self.text
	
class Row(models.Model):
	CHOICES = (
	(None, 'Your string for display'),
	('4','Excellent'),
	('3','Proficient'),
	('2','Awful'),
	('1','The worst ever'),
	)
	name = models.CharField(default="None", max_length=30)
	rubric = models.ForeignKey(Rubric)
	row_choice = models.CharField(max_length=20,choices=CHOICES, default="None", blank=True)
	excellenttext = models.TextField(default="", blank=True)
	proficienttext = models.TextField(default="", blank=True)
	satisfactorytext = models.TextField(default="", blank=True)
	unsatisfactorytext = models.TextField(default="", blank=True)
	
	def __str__(self):
		return self.row_choice
	
		
class Enrollment(models.Model):
	student = models.ForeignKey(Student)
	edclass = models.ForeignKey(EdClasses)
	semester = models.ForeignKey(Semester)
	#Will need to change completedrubric editable to False
	completedrubric = models.OneToOneField(Rubric, null=True, editable=False)
	rubriccompleted = models.BooleanField(default=False)
	
	def __str__(self):
		return 'Enrollment %s: %s' % (self.student, self.edclass)
	
	class Meta:
		unique_together = (("student", "edclass"))
		
	


