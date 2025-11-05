from django.test import TestCase
from django.core.exceptions import ValidationError
from users.models import UserProfile
from profiles.models import StartupProfile, Industry
from ..models import StartupProject


class StartupProjectModelsTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email="test@example.com", username="testuser", user_phone="+380123456789"
        )
        self.industry = Industry.objects.create(industry_name="TechIndustry")
        self.startup = StartupProfile.objects.create(
            user_id=self.user,
            company_name="Test Company",
            description="A test startup",
            website="http://example.com",
            industry_id=self.industry,
            location="Kyiv",
        )

    def test_create_project_success(self):
        project = StartupProject.objects.create(
            startup_profile=self.startup,
            title="Project Alpha",
            likes=5,
            description="Project description",
            status="Active",
        )
        self.assertEqual(project.startup_profile, self.startup)
        self.assertEqual(project.title, "Project Alpha")
        self.assertEqual(project.likes, 5)
        self.assertEqual(project.description, "Project description")
        self.assertEqual(project.status, "Active")
        self.assertIsNotNone(project.created_at)
        self.assertEqual(str(project), "Project Alpha")

    def test_create_project_fail_missing_title(self):
        project = StartupProject(
            startup_profile=self.startup, likes=5, description="Missing title", status="Inactive"
        )
        with self.assertRaises(ValidationError):
            project.full_clean()