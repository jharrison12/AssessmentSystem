from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import sys
from django.test import LiveServerTestCase, Client
from django.contrib.auth.models import User


class FunctionalTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = 'http://' + arg.split('=')[1]
                return
        super().setUpClass()
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            super().tearDownClass()

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
