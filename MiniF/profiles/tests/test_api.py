from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import UserProfile
from profiles.models import Industry


class StartupProfileAPITest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email="test@example.com", username="testuser", user_phone="+380123456789", password="testpassword"
        )
        
        self.industry = Industry.objects.create(
            industry_name="Technology"
        )
        self.client.force_authenticate(user=self.user)

    def test_api_create_profile_success(self):
        url = reverse("startupprofile-list")
        data = {
            "user_id": self.user.id,
            "company_name": "Test Company",
            "description": "Test description",
            "website": "http://example.com",

            "industry_id": self.industry.id,
            "location": "Kyiv"

        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["company_name"], "Test Company")

    def test_api_create_profile_fail_missing_field(self):
        url = reverse("startupprofile-list")
        data = {
            "user_id": self.user.id,
            "description": "Test description",
            "website": "http://example.com",

            "industry_id": self.industry.id,
            "location": "Kyiv"

        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)


        self.assertIn("company_name", response.data)

