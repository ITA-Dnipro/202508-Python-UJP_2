from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from projects.models import StartupProject
from profiles.models import Industry, InvestorProfile
from users.models import UserProfile

User = get_user_model()

class TestInvestorPermissions(APITestCase):
    '''Test permissions for saving projects by investors'''
    def setUp(self):
        self.industry = Industry.objects.create(industry_name="Technology")
        self.investor_user = User.objects.create_user(email="investor@test.com", password="password123")
        self.investor_user = InvestorProfile.objects.create(
            user_id=self.investor_user,
            investment_focus=self.industry,
            location="Kyiv"
        )

        self.regular_user = UserProfile.objects.create_user(email='user@test.com', password='password123')
        self.project = StartupProject.objects.create(company_name='Test Project', description='description', location='Kyiv', industry_id=self.industry)
        
    def test__save_project_denied_for_not_authenticated(self):
        url = reverse('save-project', args=[self.project.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403) 

    def test_save_project_denied_for_non_investor(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('save-project', args=[self.project.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_save_project_allowed_for_investor(self):
        self.client.force_authenticate(user=self.investor_user)
        url = reverse('save-project', args=[self.project.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)