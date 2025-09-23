from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import UserProfile
from profiles.models import StartupProfile, Industry
from ..models import StartupProject


class StartupProjectAPITest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email="test@example.com", username="testuser", user_phone="+380123456789", password="testpassword"
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
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.list_url = "/api/projects/"
        self.detail_url = lambda pk: f"/api/projects/{pk}/"

    def test_create_project(self):
        data = {
            "startup_profile_id": self.startup.id,
            "title": "Project Alpha",
            "likes": 10,
            "description": "Project description",
            "status": "Active",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Project Alpha")

    def test_get_project_list(self):
        StartupProject.objects.create(
            startup_profile_id=self.startup,
            title="Project Beta",
            likes=5,
            description="Another project",
            status="Active",
        )
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_project_detail(self):
        project = StartupProject.objects.create(
            startup_profile_id=self.startup,
            title="Project Gamma",
            likes=2,
            description="Gamma project",
            status="Inactive",
        )
        response = self.client.get(self.detail_url(project.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Project Gamma")

    def test_update_project(self):
        project = StartupProject.objects.create(
            startup_profile_id=self.startup,
            title="Project Delta",
            likes=0,
            description="Delta project",
            status="Active",
        )
        data = {
            "startup_profile_id": self.startup.id,
            "title": "Project Alpha",
            "likes": 15,
            "description": "Project description",
            "status": "Completed",
        }
        response = self.client.put(self.detail_url(project.id), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["likes"], 15)
        self.assertEqual(response.data["status"], "Completed")

    def test_delete_project(self):
        project = StartupProject.objects.create(
            startup_profile_id=self.startup,
            title="Project Epsilon",
            likes=3,
            description="Epsilon project",
            status="Active",
        )
        response = self.client.delete(self.detail_url(project.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StartupProject.objects.filter(id=project.id).exists())
