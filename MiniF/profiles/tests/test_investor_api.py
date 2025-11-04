from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import UserProfile
from ..models import InvestorProfile, Industry


class InvestorProfileAPITest(APITestCase):
    """A test suite for the InvestorProfile API."""
    
    def setUp(self):
        """Initialize test data before each test."""
        self.user = UserProfile.objects.create_user(email="user@example.com", username="user1", password="password123")
        self.industry = Industry.objects.create(industry_name="Technology")
        self.client.force_authenticate(user=self.user)

        self.list_url = reverse("profiles:investorprofile-list")
        self.detail_url = lambda pk: reverse("profiles:investorprofile-detail", kwargs={'pk': pk})

    def test_create_investorprofile(self):
        """Test creating a new investor profile."""
        profile = InvestorProfile.objects.create(
            user_id=self.user,
            investment_focus=self.industry,
            location="Kyiv"
        )
        self.assertEqual(profile.user_id, self.user)
        self.assertEqual(profile.investment_focus, self.industry)
        self.assertEqual(profile.location, "Kyiv")
        
    def test_get_investorprofiles_list(self):
        """Test retrieving a list of investor profiles."""
        InvestorProfile.objects.create(user_id=self.user, investment_focus=self.industry, location="Kyiv")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user_id"], self.user.id)

    def test_get_investorprofile_detail(self):
        """Test retrieving a single investor profile."""
        profile = InvestorProfile.objects.create(user_id=self.user, investment_focus=self.industry, location="Kyiv")
        response = self.client.get(self.detail_url(profile.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], profile.id)
        self.assertEqual(response.data["location"], "Kyiv")

    def test_update_investorprofile(self):
        """Test updating an investor profile."""
        profile = InvestorProfile.objects.create(user_id=self.user, investment_focus=self.industry, location="Kyiv")
        data = {
            "investment_focus": self.industry.id,
            "location": "Lviv"
        }
        response = self.client.put(self.detail_url(profile.pk), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["location"], "Lviv")

    def test_delete_investorprofile(self):
        """Test deleting an investor profile."""
        profile = InvestorProfile.objects.create(user_id=self.user, investment_focus=self.industry, location="Kyiv")
        response = self.client.delete(self.detail_url(profile.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(InvestorProfile.objects.filter(id=profile.id).exists())