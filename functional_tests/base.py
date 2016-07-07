from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import sys
from django.test import LiveServerTestCase

class FunctionalTest(LiveServerTestCase):
	
	def setUp(self):
		self.browser = webdriver.Chrome()
		self.browser.implicitly_wait(4)
	
	def tearDown(self):
		self.browser.refresh()
		self.browser.quit()

	
