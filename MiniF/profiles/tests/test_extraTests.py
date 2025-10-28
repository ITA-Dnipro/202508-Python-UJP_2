import unittest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status

from profiles.models import Industry, StartupProfile, InvestorProfile
from profiles.serializers import (
    StartupProfileSerializer,
    StartupProfileCreateSerializer,
    InvestorProfileCreateSerializer,
)


User = get_user_model()


class StartupProfileSerializerFieldValidationTests(TestCase):
    """tests for field validation in StartupProfileSerializer."""

    def setUp(self):
        self.user = User.objects.create_user(email="u1@example.com", username="u1", password="x")
        self.industry = Industry.objects.create(industry_name="Tech")

    def test_company_name_cannot_be_empty(self):
        """company_name must not be empty (field-level validation)."""
        ser = StartupProfileSerializer(
            data={
                "user_id": self.user.id,
                "company_name": "", 
                "description": "desc",
                "website": None,
                "industry_id": self.industry.id,
                "location": "Kyiv",
            }
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("company_name", ser.errors)


class OneProfilePerUserSerializerRuleTests(TestCase):
    """Minimal tests for 'one profile per user' rule in create serializers."""

    def setUp(self):
        self.user = User.objects.create_user(email="u2@example.com", username="u2", password="x")
        self.industry = Industry.objects.create(industry_name="AI")
        self.factory = APIRequestFactory()

    def test_startup_profile_create_disallows_duplicate(self):
        """StartupProfileCreateSerializer should reject a second profile for the same user."""
        StartupProfile.objects.create(
            user_id=self.user,
            company_name="FirstCo",
            description="d",
            website=None,
            industry_id=self.industry,
            location="Kyiv",
        )
        request = self.factory.post("/profiles/startup/")
        request.user = self.user

        ser = StartupProfileCreateSerializer(
            data={
                "company_name": "SecondCo",
                "description": "x",
                "website": None,
                "industry_id": self.industry.id,
                "location": "Kyiv",
            },
            context={"request": request},
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        with self.assertRaises(Exception):
            ser.save()

    def test_investor_profile_create_disallows_duplicate(self):
        """InvestorProfileCreateSerializer should reject a second profile for the same user."""
        InvestorProfile.objects.create(
            user_id=self.user,
            investment_focus=self.industry,
            location="Kyiv",
        )
        request = self.factory.post("/profiles/investor/")
        request.user = self.user

        ser = InvestorProfileCreateSerializer(
            data={"investment_focus": self.industry.id, "location": "Kyiv"},
            context={"request": request},
        )
        self.assertTrue(ser.is_valid(), ser.errors)
        with self.assertRaises(Exception):
            ser.save()


class StartupProfileViewSetFilteringTests(APITestCase):
    """
    tests that the list endpoint respects ?industry=... and ?location=...
    Uses force_authenticate to bypass auth complexity.
    """

    def setUp(self):
    
        self.user_tech = User.objects.create_user(
            email="tech@example.com", username="tech_user", password="x"
        )
        
        self.user_bio = User.objects.create_user(
            email="bio@example.com", username="bio_user", password="x"
        )

        
        self.client.force_authenticate(user=self.user_tech)

        
        self.ind_tech = Industry.objects.create(industry_name="Tech")
        self.ind_bio = Industry.objects.create(industry_name="Biotech")

        
        StartupProfile.objects.create(
            user_id=self.user_tech,  
            company_name="TechKyiv",
            description="",
            website=None,
            industry_id=self.ind_tech,
            location="Kyiv",
        )
        
        StartupProfile.objects.create(
            user_id=self.user_bio,  
            company_name="BioLviv",
            description="",
            website=None,
            industry_id=self.ind_bio,
            location="Lviv",
        )

        self.list_url = "/profiles/startups/"

    def test_filter_by_industry_case_insensitive(self):
        """?industry=tech should return only Tech industry profiles."""
        res = self.client.get(self.list_url, {"industry": "tech"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = {p["company_name"] for p in res.data}
        self.assertIn("TechKyiv", names)
        self.assertNotIn("BioLviv", names)

    def test_filter_by_location_case_insensitive(self):
        """?location=lviv should return only Lviv profiles."""
        res = self.client.get(self.list_url, {"location": "lviv"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = {p["company_name"] for p in res.data}
        self.assertIn("BioLviv", names)
        self.assertNotIn("TechKyiv", names)
