from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from projects.models import StartupProject
from profiles.models import Industry, InvestorProfile, StartupProfile, SavedProject
from users.models import UserProfile 

User = get_user_model()

class TestInvestorPermissions(APITestCase):
    '''Test permissions for saving projects by investors'''
    def setUp(self):
        self.industry = Industry.objects.create(industry_name="Technology")
        self.investor_user = User.objects.create_user(username="investor", email="investor@test.com", password="password123")
        self.investor_user.role = "investor" 
        self.investor_user.save()

        self.investor_profile = InvestorProfile.objects.create(
            user_id=self.investor_user,
            investment_focus=self.industry,
            location="Kyiv"
        )

        self.regular_user = User.objects.create_user(username='user', email='user@test.com', password='password123')
        self.regular_user.role = "regular" 
        self.regular_user.save()
        
        self.startup_user = User.objects.create_user(username='startup', email='startup@test.com', password='password123')
        self.startup_profile = StartupProfile.objects.create(
            user_id=self.startup_user,
            company_name='Test Company',
            description='Test Startup Description',
            website='http://test.com',
            industry_id=self.industry,
            location='Kyiv'
        )

        self.project = StartupProject.objects.create(
            startup_profile=self.startup_profile,
            title='Test Project Title', 
            description='description',
            status='In progress'
        )
        
        self.save_project_url = reverse('profiles:save-project', args=[self.project.id])
        
    def test__save_project_denied_for_not_authenticated(self):
        '''Checks that unauthenticated users cannot save projects and get 401 response'''
        url = self.save_project_url
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401) 

    def test_save_project_denied_for_non_investor(self):
        '''Checks that startup users cannot save projects and get 403 response'''
        self.client.force_authenticate(user=self.regular_user)
        url = self.save_project_url
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_save_project_allowed_for_investor(self):
        '''Checks that investor users can save projects successfully'''
        self.client.force_authenticate(user=self.investor_user)
        url = self.save_project_url
        initial_saved_count = SavedProject.objects.count()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SavedProject.objects.count(), initial_saved_count + 1)
        saved_project_exists = SavedProject.objects.filter(
            investor=self.investor_profile, 
            project=self.project
        ).exists()
        self.assertTrue(saved_project_exists)