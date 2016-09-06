from django.test import TestCase
from rubricapp.forms import RubricForm,RowForm,RowFormSet
from django.http import HttpRequest
from rubricapp.models import Row, Rubric

class RubricFormTest(TestCase):

	def test_form_renders_item_text_input(self):
		form = RowForm()
		#self.assertIn('placeholder="Enter a name"', form.as_p())
		self.assertIn('Excellent', form.as_p())	
		
		

		
		
	
