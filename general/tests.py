
from master_pol.cookiecutter_const import PROJECT_NAME_RUS
from django.test import TestCase
from django.utils.html import escape
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import Keys



from accounts.models import User


class HomePageTest(TestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(username='testuser', password='testpass')
        

    def test_home_page_contains_project_name(self):
        """
        На странице home присутствует ли название проекта?
        """
        
        self.client.login(username='testuser', password='testpass')
        
        response = self.client.get(reverse('home'))
        html = response.content.decode("utf8")
        self.assertIn(escape(PROJECT_NAME_RUS), html)

    def test_user_can_be_created(self):
        """
        Если программно сохранить в БД нового пользователя,
        он должен присутствовать в БД. Так ли это?
        """
        User.objects.create_user(username='foo', password='bar')
        selected_user = bool(User.objects.filter(username='foo'))
        self.assertEqual(selected_user, True)

class SeleniumHomePageTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='selenium_user', password='selenium_pass')
        self.selenium.get(self.live_server_url + reverse("login"))
        username_field = self.selenium.find_element(By.ID, "username")
        password_field = self.selenium.find_element(By.ID, "password")
        username_field.send_keys('selenium_user')
        password_field.send_keys('selenium_pass')
        password_field.send_keys(Keys.RETURN)
        WebDriverWait(self.selenium, 10).until(
            lambda driver: "login" not in driver.current_url
        )

    def test_logo_exists_on_home(self):
        """
        На странице home присутствует логотип. Так ли это?
        """
        self.selenium.get(self.live_server_url + reverse('home'))
        logo = self.selenium.find_element(By.ID, "logo")
        self.assertTrue(logo.is_displayed())

