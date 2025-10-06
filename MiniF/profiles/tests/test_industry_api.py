from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import UserProfile
from ..models import Industry


class IndustryAPITestCase(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(email="user@example.com", username="user1", password="password123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.list_url = "/api/profiles/industries/"
        self.detail_url = lambda pk: f"/api/profiles/industries/{pk}/"

    def test_create_industry(self):
        data = {"industry_name": "Technology"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["industry_name"], "Technology")

    def test_get_industries_list(self):
        Industry.objects.create(industry_name="Finance")
        Industry.objects.create(industry_name="Healthcare")
        response = self.client.get(self.list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_industry_detail(self):
        industry = Industry.objects.create(industry_name="Agriculture")
        response = self.client.get(self.detail_url(industry.id), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["industry_name"], "Agriculture")

    def test_update_industry(self):
        industry = Industry.objects.create(industry_name="Construction")
        data = {"industry_name": "Real Estate"}
        response = self.client.put(self.detail_url(industry.id), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        industry.refresh_from_db()
        self.assertEqual(industry.industry_name, "Real Estate")

    def test_delete_industry(self):
        industry = Industry.objects.create(industry_name="Tourism")
        response = self.client.delete(self.detail_url(industry.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Industry.objects.count(), 0)
