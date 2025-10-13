import pytest_
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import UserProfile
from profiles.models import InvestorProfile, SavedProject, StartupProfile, Industry
from projects.models import StartupProject

@pytest.mark.django_db
def test_unsave_project_decrements_likes():
    user = UserProfile.objects.create_user(email="user@test.com", password="password123")
    investor = InvestorProfile.objects.create(
        user_id=user,
        investment_focus=Industry.objects.create(industry_name="Tech"),
        location="Kyiv"
    )
    project = StartupProject.objects.create(
        company_name="Test Project",
        description="A test project",
        location="Kyiv",
        industry_id=investor.investment_focus
    )
    saved = SavedProject.objects.create(investor=investor, project=project)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("unsave-project", args=[project.id])
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    project.refresh_from_db()
    assert project.likes_count == 4
    assert not SavedProject.objects.filter(id=saved.id).exists()

@pytest.mark.django_db
def test_unsave_project_not_found():
    user = UserProfile.objects.create_user(email="user@test.com", password="password123")
    investor = InvestorProfile.objects.create(
        user_id=user,
        investment_focus=Industry.objects.create(industry_name="Tech"),
        location="Kyiv"
    )
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("unsave-project", args=[99999])  
    response = client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "Project not saved"
