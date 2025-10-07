from django.test import TestCase
from users.models import UserProfile


class UserProfileModelTest(TestCase):
    def test_create_user_success(self):
        user = UserProfile.objects.create_user(
            email="user@example.com", username="testuser", password="password123", user_phone="+380123456789"
        )
        self.assertEqual(user.email, "user@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.user_phone, "+380123456789")
        self.assertTrue(user.check_password("password123"))
        self.assertEqual(str(user), "user@example.com")
