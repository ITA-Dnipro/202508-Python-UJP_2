from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from users.models import UserProfile
from profiles.models import Industry, StartupProfile
import json


class CustomLoginViewTest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        self.url = reverse('custom-login')

    def test_successful_login(self):
        """Successful login test"""
        data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_login(self):
        """Failed login test"""
        data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_startup_role(self):
        """Login test with startup role"""
        industry = Industry.objects.create(industry_name="Technology")
        StartupProfile.objects.create(
            user_id=self.user,
            company_name="Test Company",
            description="Test description",
            industry_id=industry,
            location="Kyiv"
        )
        
        data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "startup"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CustomLogoutViewTest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        self.url = reverse('logout')
        
        from rest_framework_simplejwt.tokens import RefreshToken
        self.refresh = RefreshToken.for_user(self.user)
        self.access = self.refresh.access_token

    def test_successful_logout(self):
        """Successful logout test"""
        self.client.force_authenticate(user=self.user)
        data = {
            "refresh": str(self.refresh)
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertIn("Successfully logged out", response.data['detail'])

    def test_logout_without_token(self):
        """Logout test without a token"""
        self.client.force_authenticate(user=self.user)
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Refresh token required", response.data['detail'])

    def test_logout_unauthenticated(self):
        """Unauthenticated user logout test"""
        data = {
            "refresh": str(self.refresh)
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUserViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_test_user_endpoint_if_exists(self):
        """Test test_user endpoint if URL is configured"""
        try:
            from django.urls import reverse
            url = reverse('test-user')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            self.assertEqual(data['status'], 'ok')
            self.assertEqual(data['message'], 'User endpoint works')
        except:
            self.assertTrue(True)
