from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from ..models import StartupProfile, Industry
from django.contrib.auth import get_user_model

User = get_user_model()


class StartupProfileAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="apiuser", password="pass")
        self.industry = Industry.objects.create(industry_name="TechIndustry")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_profile(self):
        url = reverse("startupprofile-list")
        data = {
            "user_id": self.user.id,
            "company_name": "API Test Company",
            "description": "Test description",
            "website": "http://example.com",
            "industry_id": self.industry.id,
            "location": "Kyiv",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["company_name"], "API Test Company")

    def test_get_profile_list(self):
        StartupProfile.objects.create(
            user_id=self.user,
            company_name="Existing Company",
            description="Existing description",
            website="http://example.com",
            industry_id=self.industry,
            location="Kyiv",
        )
        url = reverse("startupprofile-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_profile_detail(self):
        profile = StartupProfile.objects.create(
            user_id=self.user,
            company_name="Detail Company",
            description="Detail description",
            website="http://example.com",
            industry_id=self.industry,
            location="Kyiv",
        )
        url = reverse("startupprofile-detail", args=[profile.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["company_name"], "Detail Company")

    def test_update_profile(self):
        profile = StartupProfile.objects.create(
            user_id=self.user,
            company_name="Old Name",
            description="Old description",
            website="http://example.com",
            industry_id=self.industry,
            location="Kyiv",
        )
        url = reverse("startupprofile-detail", args=[profile.id])
        data = {"company_name": "New Name"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["company_name"], "New Name")

    def test_delete_profile(self):
        profile = StartupProfile.objects.create(
            user_id=self.user,
            company_name="Delete Me",
            description="To be deleted",
            website="http://example.com",
            industry_id=self.industry,
            location="Kyiv",
        )
        url = reverse("startupprofile-detail", args=[profile.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StartupProfile.objects.filter(id=profile.id).exists())
