from django import forms
from django.forms import ModelForm, formset_factory, modelformset_factory, inlineformset_factory
from rubricapp.models import Rubric, Row


class RowForm(ModelForm):
	class Meta:
		model = Row
		fields = ['row_choice']
		
class RubricForm(ModelForm):
	class Meta:
		model = Rubric
		fields = ['name']

RowFormSet = modelformset_factory(Row, fields=('row_choice',), extra=0) #extra=0 keeps the formset from creating new form
