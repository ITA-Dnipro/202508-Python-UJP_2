from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from ..models import Industry


class IndustryModelTest(TestCase):
    def test_create_industry(self):
        industry = Industry.objects.create(industry_name="Technology")
        self.assertEqual(industry.industry_name, "Technology")
        self.assertEqual(str(industry), "Technology")

    def test_unique_industry_name(self):
        Industry.objects.create(industry_name="Finance")
        with self.assertRaises(IntegrityError):
            Industry.objects.create(industry_name="Finance")

    def test_max_length_constraint(self):
        long_name = "A" * 256
        industry = Industry(industry_name=long_name)
        with self.assertRaises(ValidationError):
            industry.full_clean()
