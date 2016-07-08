from django.db import models

class Semester(models.Model):
	text = models.TextField(default='201530')
	
	def __str__(self):
		return self.text

class EdClasses(models.Model):
	name = models.TextField(default='')
	semester = models.ForeignKey(Semester, default=None)

	def __str__(self):
		return self.name

class Student(models.Model):
	name = models.TextField(default="")	
