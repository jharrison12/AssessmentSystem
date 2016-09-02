from django.test import TestCase
from rubricapp.forms import RubricForm,RowForm,RowFormSet
from django.http import HttpRequest
from rubricapp.models import Row, Rubric

class RubricFormTest(TestCase):

	def test_form_renders_item_text_input(self):
		form = RowForm()
		#self.assertIn('placeholder="Enter a name"', form.as_p())
		self.assertIn('Excellent', form.as_p())	
		
	def test_rubric_form_will_not_take_null_value(self):
		#request = HttpRequest()
		testrubric = Rubric.objects.create()
		testrow = Row.objects.create(rubric=testrubric)
		rowformtest = RowForm({'row_choice':0})
		self.assertEqual(rowformtest.is_valid(), False)
		
		

		
		
	
