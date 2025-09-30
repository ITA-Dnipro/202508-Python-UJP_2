from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ValidationError
from users.serializers import UserRegistrationSerializer, CustomLoginSerializer
from users.models import UserProfile
from profiles.models import StartupProfile, InvestorProfile, Industry


class UserRegistrationSerializerTest(TestCase):
    def test_valid_registration_data(self):
        """Valid registration data test"""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "password2": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
            "user_phone": "+380123456789"
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_password_mismatch(self):
        """Password mismatch test"""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "password2": "differentpassword",
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Passwords do not match.", str(serializer.errors))

    def test_create_user(self):
        """Test user creation via serializer"""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "password2": "testpassword123",
            "first_name": "Test",
            "user_phone": "+380123456789"
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertTrue(user.check_password("testpassword123"))


class CustomLoginSerializerTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        self.industry = Industry.objects.create(industry_name="Technology")
        
    def test_valid_login(self):
        """Successful login test"""
        data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        serializer = CustomLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        validated_data = serializer.validated_data
        self.assertIn("access", validated_data)
        self.assertIn("refresh", validated_data)

    def test_invalid_credentials(self):
        """Invalid credentials test"""
        data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        serializer = CustomLoginSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_startup_role_validation_success(self):
        """Successful startup role validation test"""
        StartupProfile.objects.create(
            user_id=self.user,
            company_name="Test Company",
            description="Test description",
            industry_id=self.industry,
            location="Kyiv"
        )
        
        data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "startup"
        }
        serializer = CustomLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_startup_role_validation_fail(self):
        """Startup role validation failed test"""
        data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "startup"
        }
        serializer = CustomLoginSerializer(data=data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("User is not a startup", str(context.exception))