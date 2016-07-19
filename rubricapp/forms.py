from django import forms

class RubricForm(forms.Form):
	CHOICES = (('1', 'Excellent',), ('2', 'Quite Awful',),('3', "Abysmal",),("4", "No"))
	name = "Writing Rubric"
	row1 = forms.ChoiceField(
		widget=forms.Select, choices=CHOICES
		)
	row2 = forms.ChoiceField(
		widget=forms.Select, choices=CHOICES
		)
	row3 = forms.ChoiceField(
		widget=forms.Select, choices=CHOICES
		)
	row4 = forms.ChoiceField(
		widget=forms.Select, choices=CHOICES
		)