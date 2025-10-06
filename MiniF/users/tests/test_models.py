from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class UserProfileModelTest(TestCase):
    def test_create_user_success(self):
        """Test for successful user creation"""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpassword123",
            user_phone="+380123456789"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.user_phone, "+380123456789")
        self.assertTrue(user.check_password("testpassword123"))

    def test_create_user_with_empty_email(self):
        """Test that user can be created with empty email (Django default behavior)"""
        user = User.objects.create_user(
            email="",
            username="testuser", 
            password="testpassword123"
        )
        self.assertEqual(user.email, "")
        self.assertEqual(user.username, "testuser")
            
    def test_create_user_with_none_email(self):
        """Test that user can be created with None email (converts to empty string)"""
        user = User.objects.create_user(
            email=None,
            username="testuser",
            password="testpassword123"
        )
        self.assertEqual(user.email, "")  
        self.assertEqual(user.username, "testuser")

    def test_email_uniqueness(self):
        """Email uniqueness test"""
        User.objects.create_user(
            email="test@example.com",
            username="testuser1",
            password="testpassword123"
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="test@example.com",
                username="testuser2",
                password="testpassword123"
            )

    def test_str_method(self):
        """Test of the string representation of the model"""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        self.assertEqual(str(user), "test@example.com")

    def test_username_field_is_email(self):
        """Test that USERNAME_FIELD is set to email"""
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_required_fields(self):
        """Required fields test"""
        self.assertEqual(User.REQUIRED_FIELDS, ["username"])