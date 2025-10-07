from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import UserProfile
from ..models import InvestorProfile, Industry


class InvestorProfileAPITest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(email="user@example.com", username="user1", password="password123")
        self.industry = Industry.objects.create(industry_name="Technology")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.list_url = "/api/profiles/investor-profiles/"
        self.detail_url = lambda pk: f"/api/profiles/investor-profiles/{pk}/"

    def test_create_investorprofile(self):
        data = {"user_id": self.user.id, "investment_focus": self.industry.id, "location": "Kyiv"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertEqual(response.data["investment_focus"], self.industry.id)
        self.assertEqual(response.data["location"], "Kyiv")

    def test_get_investorprofiles_list(self):
        InvestorProfile.objects.create(user_id=self.user, investment_focus=self.industry, location="Kyiv")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user_id"], self.user.id)

    def test_get_investorprofile_detail(self):
        profile = InvestorProfile.objects.create(user_id=self.user, investment_focus=self.industry, location="Kyiv")
        response = self.client.get(self.detail_url(profile.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], profile.id)
        self.assertEqual(response.data["location"], "Kyiv")

    def test_update_investorprofile(self):
        profile = InvestorProfile.objects.create(user_id=self.user, investment_focus=self.industry, location="Kyiv")
        data = {"user_id": self.user.id, "investment_focus": self.industry.id, "location": "Lviv"}
        response = self.client.put(self.detail_url(profile.pk), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["location"], "Lviv")

    def test_delete_investorprofile(self):
        profile = InvestorProfile.objects.create(user_id=self.user, investment_focus=self.industry, location="Kyiv")
        response = self.client.delete(self.detail_url(profile.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(InvestorProfile.objects.filter(id=profile.id).exists())
