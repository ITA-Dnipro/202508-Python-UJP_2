from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="login@example.com", username="loginuser", password="secret123"
        )

    def test_custom_login_ok(self):
        url = reverse("custom-login")
        res = self.client.post(url, {"email": "login@example.com", "password": "secret123"}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("refresh", res.data)
        self.assertIn("access", res.data)
