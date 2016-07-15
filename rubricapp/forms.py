from django import forms

class RubricForm(forms.Form):
	CHOICES = (('1', 'Excellent',), ('2', 'Quite Awful',))
	item_text = forms.CharField(
		widget=forms.fields.TextInput(attrs={
			'placeholder': 'Enter a name',
			}),
	)
	student_score = forms.ChoiceField(
		widget=forms.Select, choices=CHOICES
		)
