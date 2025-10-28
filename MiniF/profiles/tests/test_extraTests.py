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


