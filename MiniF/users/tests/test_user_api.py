from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import UserProfile


class UserProfileAPITest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email="user@example.com", username="testuser", password="password123", user_phone="+380123456789"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.list_url = "/api/users/"
        self.detail_url = lambda pk: f"/api/users/{pk}/"

    def test_create_user(self):
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123",
            "user_phone": "+380987654321",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "newuser@example.com")

    def test_get_user_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(u["email"] == self.user.email for u in response.data))

    def test_get_user_detail(self):
        response = self.client.get(self.detail_url(self.user.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_update_user(self):
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123",
            "user_phone": "+380111222333",
        }
        response = self.client.put(self.detail_url(self.user.pk), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_phone"], "+380111222333")

    def test_delete_user(self):
        response = self.client.delete(self.detail_url(self.user.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
