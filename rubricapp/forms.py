from django import forms

class RubricForm(forms.Form):
	item_text = forms.CharField(
		widget=forms.fields.TextInput(attrs={
			'placeholder': 'Enter a name',
			}),
	)
