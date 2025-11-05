from rest_framework.test import APITestCase
from rest_framework import status
from users.models import UserProfile
from profiles.models import StartupProfile, Industry
from ..models import StartupProject
from django.urls import reverse


class StartupProjectAPITest(APITestCase):
    """A test suite for the StartupProject API."""

    def setUp(self):
        """Initialize test data before each test."""
        self.user = UserProfile.objects.create_user(
            email="test@example.com",
            username="testuser",
            user_phone="+380123456789",
            password="testpassword"
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
        self.client.force_authenticate(user=self.user)

        self.list_url = reverse("startupproject-list")
        self.detail_url = lambda pk: reverse("startupproject-detail", kwargs={'pk': pk})

    def test_create_project(self):
        """Test creating a new startup project via API."""
        data = {
            "startup_profile_id": self.startup.id,
            "title": "Project Alpha",
            "description": "Project description",
            "status": "Active",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Project Alpha")

    def test_get_project_list(self):
        """Test retrieving a list of all startup projects."""
        StartupProject.objects.create(
            startup_profile=self.startup,
            title="Project Beta",
            description="Another project",
            status="Active",
        )
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_project_detail(self):
        """Test retrieving the details of a specific startup project."""
        project = StartupProject.objects.create(
            startup_profile=self.startup,
            title="Project Gamma",
            description="Gamma project",
            status="Inactive",
        )
        response = self.client.get(self.detail_url(project.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Project Gamma")

    def test_update_project(self):
        """Test updating a startup project's data."""
        project = StartupProject.objects.create(
            startup_profile=self.startup,
            title="Project Delta",
            description="Delta project",
            status="Active",
        )
        data = {
            "startup_profile_id": self.startup.id,
            "title": "Project Delta Updated",
            "description": "Updated description",
            "status": "Completed",
        }
        response = self.client.put(self.detail_url(project.id), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "Completed")

    def test_delete_project(self):
        """Test deleting a startup project."""
        project = StartupProject.objects.create(
            startup_profile=self.startup,
            title="Project Epsilon",
            description="Epsilon project",
            status="Active",
        )
        response = self.client.delete(self.detail_url(project.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StartupProject.objects.filter(id=project.id).exists())
