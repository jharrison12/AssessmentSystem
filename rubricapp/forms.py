from django import forms
from django.forms import ModelForm, formset_factory, modelformset_factory, inlineformset_factory
from rubricapp.models import Rubric, Row
from django.contrib.auth.models import User
from django.core.exceptions import NON_FIELD_ERRORS

class RowForm(ModelForm):
	class Meta:
		model = Row
		fields = ['row_choice', 'excellenttext','proficienttext', 'satisfactorytext','unsatisfactorytext']

class RubricForm(ModelForm):
	class Meta:
		model = Rubric
		fields = ['name']
		error_messages = {
			NON_FIELD_ERRORS: {
				'unique': "This rubric has already been completed"
			}
		}

RowFormSet = modelformset_factory(Row, fields=('row_choice','excellenttext','proficienttext','satisfactorytext', 'unsatisfactorytext'), extra=0) #extra=0 keeps the formset from creating new form

