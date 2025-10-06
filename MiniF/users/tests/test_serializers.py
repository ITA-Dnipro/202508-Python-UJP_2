from django.test import TestCase
from rest_framework.test import APIRequestFactory
from users.serializers import UserRegistrationSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from users.serializers import PasswordResetConfirmSerializer

class UserRegistrationSerializerTest(TestCase):
    def test_create_user(self):
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "user_phone": "+380123456789",
            "password": "testpassword123",
            "password2": "testpassword123",
        }
        factory = APIRequestFactory()
        request = factory.post("/api/auth/registration/", data, format="json")

        serializer = UserRegistrationSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save(request)
        self.assertEqual(user.email, data["email"])
        self.assertTrue(user.check_password(data["password"]))
        


User = get_user_model()

class PasswordResetConfirmSerializerTest(TestCase):
    def test_reset_password_ok(self):
        user = User.objects.create_user(
            email="pw@example.com", username="pw", password="oldpass123"
        )
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        data = {
            "uidb64": uidb64,
            "token": token,
            "new_password1": "newpass1234",
            "new_password2": "newpass1234",
        }

        ser = PasswordResetConfirmSerializer(data=data)
        self.assertTrue(ser.is_valid(), ser.errors)
        saved = ser.save()
        self.assertEqual(saved.pk, user.pk)
        self.assertTrue(saved.check_password("newpass1234"))
