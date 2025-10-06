from django.test import TestCase
from users.models import UserProfile
from django.core.exceptions import ValidationError
from ..models import InvestorProfile, Industry


class InvestorProfileModelTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email="user@example.com", username="user1", password="password123"
        )
        self.industry = Industry.objects.create(industry_name="Technology")

    def test_create_investorprofile_success(self):
        profile = InvestorProfile.objects.create(user_id=self.user, investment_focus=self.industry, location="Kyiv")
        self.assertEqual(profile.user_id, self.user)
        self.assertEqual(profile.investment_focus, self.industry)
        self.assertEqual(profile.location, "Kyiv")
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)
        self.assertEqual(str(profile), self.user.email)

    def test_create_investorprofile_fail(self):
        profile = InvestorProfile(user_id=self.user, investment_focus=self.industry, location=None)
        with self.assertRaises(ValidationError):
            profile.full_clean()
