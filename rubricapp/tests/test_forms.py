from django.test import TestCase
from rubricapp.forms import RubricForm

class RubricFormTest(TestCase):

	def test_form_renders_item_text_input(self):
		form = RubricForm()
		self.assertIn('placeholder="Enter a name"', form.as_p())
		self.assertIn('Excellent', form.as_p())	
