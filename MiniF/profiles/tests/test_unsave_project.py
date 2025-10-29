from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase 
from users.models import UserProfile
from profiles.models import InvestorProfile, SavedProject, StartupProfile, Industry
from projects.models import StartupProject

class TestUnsaveProject(APITestCase):
    '''Tests for the functionality of removing a saved project by an investor'''
    
    def setUp(self):
        self.industry = Industry.objects.create(industry_name="Tech")
        
        startup = UserProfile.objects.create_user(username="startup", email="startup@test.com", password="password123")
        self.startup_profile = StartupProfile.objects.create(
            user_id=startup,
            company_name='Test Company',
            description='Test Startup Description',
            website='http://test.com',
            industry_id=self.industry,
            location='Kyiv'
        )
        self.project = StartupProject.objects.create(
            startup_profile_id=self.startup_profile,
            title='Test Project Title', 
            description="A test project",
            status='Concept',
            likes=1 
        )
        
        self.user = UserProfile.objects.create_user(username="investor_user", email="user@test.com", password="password123")
        self.user.role = "investor" 
        self.investor = InvestorProfile.objects.create(
            user_id=self.user,
            investment_focus=self.industry,
            location="Kyiv"
        )
        self.saved_project = SavedProject.objects.create(investor=self.investor, project=self.project)
        
        self.unsave_url = reverse("profiles:unsave-project", args=[self.saved_project.id])
        self.not_found_url = reverse("profiles:unsave-project", args=[999999999999999999999]) 

    def test_unsave_project_decrements_likes(self):
        '''Checks that deleting a saved project decreases the like counter'''

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.unsave_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.project.refresh_from_db()
        self.assertEqual(self.project.likes, 0)

        saved_exists = SavedProject.objects.filter(id=self.saved_project.id).exists()
        self.assertFalse(saved_exists)


    def test_unsave_project_not_found(self):
        '''Checks that deleting a non-existing SavedProject returns 404'''

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.not_found_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No SavedProject matches the given query.")