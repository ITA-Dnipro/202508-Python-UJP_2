from django.test import TestCase
from ..models import StartupProfile, Industry
from django.contrib.auth import get_user_model

User = get_user_model()


class StartupProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.industry = Industry.objects.create(industry_name="TechIndustry")

    def test_profile_creation(self):
        profile = StartupProfile.objects.create(
            user_id=self.user,
            company_name="Test Company",
            description="A test startup",
            website="http://example.com",
            industry_id=self.industry,
            location="Kyiv",
        )
        self.assertEqual(profile.company_name, "Test Company")
        self.assertEqual(profile.location, "Kyiv")
        self.assertEqual(profile.industry_id.industry_name, "TechIndustry")
