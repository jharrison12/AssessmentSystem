from django.db import models

class Student(models.Model):
	name = models.TextField(default="")	
	
	def __str__(self):
		return self.name
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

class Enrollment(models.Model):
	student = models.ForeignKey(Student)
	edclass = models.ForeignKey(EdClasses)
	grade = models.TextField(default='') 
	
