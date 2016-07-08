from django.db import models


class EdClasses(models.Model):
	name = models.TextField(default='')

	def __str__(self):
		return self.name
class Semester(models.Model):
	text = models.TextField(default='201530')
	classes = models.ManyToManyField(EdClasses)	
	def __str__(self):
		return self.text


class Student(models.Model):
	name = models.TextField(default="")	
	#TODO add models
