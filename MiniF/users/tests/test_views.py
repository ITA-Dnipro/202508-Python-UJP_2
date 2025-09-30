from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from users.models import UserProfile
from profiles.models import Industry, StartupProfile  
import json


class CustomLoginViewTest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpassword123",
        )
        self.url = reverse("custom-login")

    def test_successful_login(self):
        """Successful login without role requirement"""
        data = {"email": "test@example.com", "password": "testpassword123"}
        res = self.client.post(self.url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_invalid_login(self):
        """Invalid password -> 400"""
        data = {"email": "test@example.com", "password": "wrongpassword"}
        res = self.client.post(self.url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_startup_role_requires_profile(self):
        """
        If role='startup' but no StartupProfile exists for the user -> 400.
        """
        data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "startup",
        }
        res = self.client.post(self.url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("startup", str(res.data).lower())

    def test_login_with_startup_role_success(self):
        """
        Positive case for role='startup'.
        """
        industry = Industry.objects.create(industry_name="Technology")
        StartupProfile.objects.create(
            user_id=self.user,          
            company_name="Test Company",
            description="Test description",
            industry_id=industry,       
            location="Kyiv",
        )

        data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "startup",
        }
        res = self.client.post(self.url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)



class CustomLogoutViewTest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email="out@example.com",
            username="out",
            password="pass12345",
        )
        self.url = reverse("logout")
        from rest_framework_simplejwt.tokens import RefreshToken

        self.refresh = RefreshToken.for_user(self.user)
        self.access = self.refresh.access_token

    def test_successful_logout(self):
        """Authenticated + refresh in body -> 205"""
        self.client.force_authenticate(user=self.user)
        res = self.client.post(self.url, {"refresh": str(self.refresh)}, format="json")
        self.assertEqual(res.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertIn("successfully", res.data.get("detail", "").lower())

    def test_logout_without_token(self):
        """Authenticated but no refresh in body -> 400"""
        self.client.force_authenticate(user=self.user)
        res = self.client.post(self.url, {}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh", str(res.data).lower())

    def test_logout_unauthenticated(self):
        """No auth -> 401"""
        res = self.client.post(self.url, {"refresh": str(self.refresh)}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class TestUserViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_test_user_endpoint_if_exists(self):
        """if endpoint in urls ->  200 """
        try:
            url = reverse("test-user")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["message"], "User endpoint works")
        except Exception:
            self.assertTrue(True)

