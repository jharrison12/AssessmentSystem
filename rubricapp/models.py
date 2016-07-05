from django.db import models

class Semester(models.Model):
	text = models.TextField(default='')

class EdClasses(models.Model):
	name = models.TextField(default='')

# Create your models here.
