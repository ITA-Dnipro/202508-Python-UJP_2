from django.test import TestCase
from users.models import UserProfile
from profiles.models import StartupProfile


class StartupProfileModelsTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email="test@example.com", username="testuser", user_phone="+380123456789"
        )

    def test_startup_profile_creation_success(self):
        profile = StartupProfile.objects.create(
            user_id=self.user,
            company_name="Test Company",
            description="A test startup",
            website="http://example.com",
            industry_id=1,
            location="Kyiv",
        )
        self.assertEqual(profile.company_name, "Test Company")
        self.assertEqual(profile.website, "http://example.com")
        self.assertEqual(profile.location, "Kyiv")

    def test_startup_profile_creation_fail(self):
        with self.assertRaises(Exception):
            StartupProfile.objects.create(
                user_id=self.user,
                company_name="Test Company",
                description="Startup test",
                website="A test startup",
                location="Lviv",
            )
