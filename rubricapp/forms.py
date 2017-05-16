from django import forms
from django.forms import BaseModelFormSet, ModelForm, formset_factory, modelformset_factory, inlineformset_factory
from rubricapp.models import Rubric, Row
from django.contrib.auth.models import User
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib import auth
from django.contrib.auth.forms import PasswordChangeForm
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)
#import zxcvbn 

class RowForm(ModelForm):
	
	def clean(self):
		cleaned_data = super(RowForm, self).clean()
		row_choice = cleaned_data.get('row_choice')
		if row_choice == "0":
			raise ValidationError('You must make a choice')
	
	class Meta:
		model = Row
		fields = ['name','row_choice', 'excellenttext','proficienttext', 'satisfactorytext','unsatisfactorytext']
	
	
		
class RubricForm(ModelForm):
	class Meta:
		model = Rubric
		fields = ['name',]
		error_messages = {
			NON_FIELD_ERRORS: {
				'unique': "This rubric has already been completed"
			}
		}

		
class BaseRowFormSet(BaseModelFormSet):
	
	def clean(self):
		super(BaseRowFormSet, self).clean()
		
		for form in self.forms:
			row_choice_data = form.cleaned_data['row_choice']
			logging.critical(" THE CLEANED DATA {}".format(form.cleaned_data))
			#note: line below does not work for None.  Must be 0. 
			if form.cleaned_data['row_choice'] == '0':
				raise forms.ValidationError('You must make a choice')
		return row_choice_data
				
		
RowFormSet = modelformset_factory(Row, fields=('name','row_choice','excellenttext','proficienttext','satisfactorytext', 'unsatisfactorytext'), formset=BaseRowFormSet, extra=0) #extra=0 keeps the formset from creating new form

class PwordChangeForm(PasswordChangeForm):
	pass

