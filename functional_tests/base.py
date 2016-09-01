from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import sys
from django.test import LiveServerTestCase, Client
from django.contrib.auth.models import User

class FunctionalTest(LiveServerTestCase):
	
	def setUp(self):
		self.browser = webdriver.Chrome()
		self.client = Client()
		self.username = 'bob'
		self.email = 'test@test.com'
		self.password = 'bob'        
		self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
		self.browser.implicitly_wait(4)
	
	def tearDown(self):
		self.browser.refresh()
		self.test_user.delete()
		self.browser.quit()

	
