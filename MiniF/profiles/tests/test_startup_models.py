from django.test import TestCase
from django.core.exceptions import ValidationError
from users.models import UserProfile
from profiles.models import StartupProfile, Industry


class StartupProfileModelsTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email="test@example.com", username="testuser", user_phone="+380123456789"
        )
        self.industry = Industry.objects.create(industry_name="TechIndustry")

    def test_startup_profile_creation_success(self):
        profile = StartupProfile.objects.create(
            user_id=self.user,
            company_name="Test Company",
            description="A test startup",
            website="http://example.com",
            industry_id=self.industry,
            location="Kyiv",
        )
        self.assertEqual(profile.company_name, "Test Company")
        self.assertEqual(profile.website, "http://example.com")
        self.assertEqual(profile.location, "Kyiv")

    def test_startup_profile_creation_fail(self):
        profile = StartupProfile(
            user_id=self.user,
            company_name="Test Company",
            description="Startup test",
            website="not-a-url",
            industry_id=self.industry,
            location="Lviv",
        )
        with self.assertRaises(ValidationError):
            profile.full_clean()
