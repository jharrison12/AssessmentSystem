from django import forms
from django.forms import BaseModelFormSet, ModelForm, formset_factory, modelformset_factory, inlineformset_factory
from rubricapp.models import Rubric, Row
from django.contrib.auth.models import User
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib import auth

class RowForm(ModelForm):
	
	def clean(self):
		cleaned_data = super(RowForm, self).clean()
		row_choice = cleaned_data.get('row_choice')
		if row_choice == 0:
			raise ValidationError('You must make a choice')
	
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

		
class BaseRowFormSet(BaseModelFormSet):
	
	def clean(self):
		super(BaseRowFormSet, self).clean()
		
		for form in self.forms:
			row_choice_data = form.cleaned_data['row_choice']
			if form.cleaned_data['row_choice'] == '0' :
				raise forms.ValidationError('You must make a choice')
		return row_choice_data
				
		
RowFormSet = modelformset_factory(Row, fields=('row_choice','excellenttext','proficienttext','satisfactorytext', 'unsatisfactorytext'), formset=BaseRowFormSet, extra=0) #extra=0 keeps the formset from creating new form



## Form for validating password
class ValidatingPasswordForm(object):
	MIN_LENGTH = 10
	
	def clean_new_password1(self):
		password1 = self.cleaned_data.get('new_password1')

		# At least MIN_LENGTH long
		if len(password1) < self.MIN_LENGTH:
			raise forms.ValidationError("The new password must be at least %d characters long." % self.MIN_LENGTH)

		# At least one letter and one non-letter
		first_isalpha = password1[0].isalpha()
		if all(c.isalpha() == first_isalpha for c in password1):
			raise forms.ValidationError("The new password must contain at least one letter and at least one digit or" \
										" punctuation character.")

		# ... any other validation you want ...

		return password1
		
class ValidatingPasswordChangeForm(ValidatingPasswordForm, auth.forms.PasswordChangeForm):
	pass

class ValidatingSetPasswordForm(ValidatingPasswordForm, auth.forms.SetPasswordForm):
	pass
