from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from rest_framework.test import APITestCase

USER = "test_user"
PASSWORD = "test_pass"

STATUS_200 = HTTP_200_OK
STATUS_401 = HTTP_401_UNAUTHORIZED


class BaseTestCase(APITestCase):
    def tearDown(self):
        User.objects.all().delete()


class TestLoginView(BaseTestCase):
    """Тесты для View представления аутентификации пользователя"""

    def setUp(self):
        self.user = User.objects.create_user(username=USER, password=PASSWORD)
        self.url = reverse("authapp:sign-in")
        self.data = {"username": USER, "password": PASSWORD}

    def test_successful_login(self):
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, STATUS_200)

    def test_unsuccessful_login(self):
        self.data["password"] = "wrong_pass"
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, STATUS_401)

    def test_empty_username(self):
        self.data["username"] = ""
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, STATUS_401)

    def test_empty_password(self):
        self.data["password"] = ""
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, STATUS_401)


class TestSignUpView(BaseTestCase):
    """Тесты для View представления регистрации пользователя"""

    def setUp(self):
        self.url = reverse("authapp:sign-up")
        self.data = {"username": USER, "password": PASSWORD, "name": USER}

    def test_successful_signup(self):
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, STATUS_200)

    def test_unsuccessful_signup(self):
        self.data["password"] = ""
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)


class LogoutView(BaseTestCase):
    """Тесты для View представления выхода пользователя из аккаунта"""

    def setUp(self):
        self.url = reverse("authapp:logout")
        self.user = User.objects.create_user(username=USER, password=PASSWORD)
        self.client.force_login(user=self.user)

    def test_successful_logout(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, STATUS_200)
