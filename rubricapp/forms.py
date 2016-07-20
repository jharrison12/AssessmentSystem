from django import forms
from django.forms import ModelForm
from rubricapp.models import Rubric, Row


class RubricForm(ModelForm):
	rows = forms.ModelChoiceField(queryset=Row.objects.all())
	
	class Meta:
		model = Rubric
		fields = ['rows']
