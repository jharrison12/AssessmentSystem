from django import forms
from django.forms import ModelForm
from rubricapp.models import Rubric, Row

class RowForm(ModelForm):
	class Meta:
		model = Row
		fields = ['row_choice']
		
class RubricForm(ModelForm):
	class Meta:
		model = Rubric
		fields = ['name']