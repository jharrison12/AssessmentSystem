from django import forms
from django.forms import ModelForm, formset_factory, modelformset_factory, inlineformset_factory
from rubricapp.models import Rubric, Row
from django.contrib.auth.models import User
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib import auth

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

class ValidatingPasswordChangeForm(auth.forms.PasswordChangeForm):
	MIN_LENGTH = 8
	
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
