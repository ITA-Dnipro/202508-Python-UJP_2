from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import UserProfile
from ..models import StartupProfile, Industry

class StartupProfileAPITest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email="test@example.com",
            username="testuser",
            user_phone="+380123456789",
            password="testpassword",
        )
        self.industry = Industry.objects.create(industry_name="Technology")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.list_url = "/api/profiles/startup-profiles/"
        self.detail_url = lambda pk: f"/api/profiles/startup-profiles/{pk}/"

    def test_api_create_profile_success(self):
        data = {
            "user_id": self.user.id,
            "company_name": "Test Company",
            "description": "Test description",
            "website": "http://example.com",
            "industry_id": self.industry.id,
            "location": "Kyiv",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["company_name"], "Test Company")
        self.assertEqual(response.data["industry_id"], self.industry.id)

    def test_api_create_profile_fail_missing_field(self):
        data = {
            "user_id": self.user.id,
            "description": "Test description",
            "website": "http://example.com",
            "industry_id": self.industry.id,
            "location": "Kyiv",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company_name", response.data)

    def test_get_startup_profiles_list(self):
        StartupProfile.objects.create(
            user_id=self.user,
            company_name="Test Company",
            description="Some desc",
            website="http://example.com",
            industry_id=self.industry,
            location="Kyiv",
        )
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]["company_name"], "Test Company")

    def test_get_startup_profile_detail(self):
        profile = StartupProfile.objects.create(
            user_id=self.user,
            company_name="Test Company",
            description="Some desc",
            website="http://example.com",
            industry_id=self.industry,
            location="Kyiv",
        )
        response = self.client.get(self.detail_url(profile.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], profile.id)
        self.assertEqual(response.data["location"], "Kyiv")

    def test_update_startup_profile(self):
        profile = StartupProfile.objects.create(
            user_id=self.user,
            company_name="Test Company",
            description="Some desc",
            website="http://example.com",
            industry_id=self.industry,
            location="Kyiv",
        )
        data = {
            "user_id": self.user.id,
            "company_name": "Test Company",
            "description": "Updated desc",
            "website": "http://example.com",
            "industry_id": self.industry.id,
            "location": "Lviv",
        }
        response = self.client.put(self.detail_url(profile.pk), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], "Updated desc")
        self.assertEqual(response.data["location"], "Lviv")

    def test_delete_startup_profile(self):
        profile = StartupProfile.objects.create(
            user_id=self.user,
            company_name="Test Company",
            description="Some desc",
            website="http://example.com",
            industry_id=self.industry,
            location="Kyiv",
        )
        response = self.client.delete(self.detail_url(profile.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StartupProfile.objects.filter(id=profile.id).exists())
