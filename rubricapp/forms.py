from django import forms
from django.forms import ModelForm, formset_factory, modelformset_factory, inlineformset_factory
from rubricapp.models import Rubric, Row
from django.contrib.auth.models import User

class RowForm(ModelForm):
	class Meta:
		model = Row
		fields = ['row_choice', 'excellenttext','proficienttext', 'satisfactorytext','unsatisfactorytext']

class RubricForm(ModelForm):
	class Meta:
		model = Rubric
		fields = ['name']

RowFormSet = modelformset_factory(Row, fields=('row_choice','excellenttext','proficienttext','satisfactorytext', 'unsatisfactorytext'), extra=0) #extra=0 keeps the formset from creating new form

"""
Probably don't need the form below

class UserForm(ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ('username', 'email', 'password')
		
"""
