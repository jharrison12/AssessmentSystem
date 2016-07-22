from django.db import models

class Student(models.Model):
	firstname = models.TextField(default="")	
	lastname = models.TextField(default="")
	lnumber = models.TextField(default="")
	
	def __str__(self):
		return self.lnumber
	#TODO add models

class EdClasses(models.Model):
	name = models.TextField(default='')
	students = models.ManyToManyField(Student, through="Enrollment")
	def __str__(self):
		return self.name
		
class Semester(models.Model):
	text = models.TextField(default='201530')
	classes = models.ManyToManyField(EdClasses)	
	def __str__(self):
		return self.text
		
class Rubric(models.Model):
	name = models.TextField(default="Basic Rubric")
	
	def __str__(self):
		return self.name
	
	
class Row(models.Model):
	CHOICES = (
	(None, 'Your string for display'),
	(1,'Excellent'),
	(2,'Proficient'),
	(3,'Awful'),
	(4,'The worst ever'),
	)
	rubric = models.ForeignKey(Rubric)
	row_choice = models.CharField(max_length=20,choices=CHOICES, default="None", blank=True)
	excellenttext = models.TextField(default="")
	proficienttext = models.TextField(default="")
	satisfactorytext = models.TextField(default="")
	unsatisfactorytext = models.TextField(default="")
	
	def __str__(self):
		return self.row_choice
	
		
class Enrollment(models.Model):
	student = models.ForeignKey(Student)
	edclass = models.ForeignKey(EdClasses)
	grade = models.TextField(default='') 
	keyrubric = models.ManyToManyField(Rubric)
	

