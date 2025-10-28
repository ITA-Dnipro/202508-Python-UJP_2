from django.test import TestCase
from django.utils import timezone
from profiles.models import StartupProfile, Industry
from projects.models import StartupProject
from django.contrib.auth import get_user_model

User = get_user_model()

class StartupProjectModelTest(TestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(
            email="test@example.com", 
            username="testuser", 
            password="pass"
        )
        self.industry = Industry.objects.create(industry_name="Tech")
        self.profile = StartupProfile.objects.create(
            user_id=self.user,
            company_name="Test Company",
            description="Test description",
            website="http://test.com",
            industry_id=self.industry,
            location="Kyiv",
        )
        
    def test_project_creation(self):
        """Test StartupProject creation"""
        project = StartupProject.objects.create(
            startup_profile_id=self.profile, 
            title="Test Project", 
            description="Project description", 
            status="Active"
        )
        self.assertEqual(project.title, "Test Project")
        self.assertEqual(project.startup_profile_id, self.profile)
        self.assertEqual(project.likes, 0)
        self.assertEqual(project.status, "Active")
        self.assertIsNotNone(project.created_at)
        
        
        self.assertIsNotNone(project.updated_at)

    def test_str_method(self):
        """Test string representation"""
        project = StartupProject.objects.create(
            startup_profile_id=self.profile,
            title="Test Project",
            description="Project description",
            status="Active"
        )
        self.assertIn("Test Project", str(project.title))