# === Third-party: Django / DRF / libs ===
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from dj_rest_auth.serializers import (
    PasswordResetConfirmSerializer as DJPasswordResetConfirmSerializer,
)

# === Local imports ===
from .models import UserProfile
from profiles.models import StartupProfile, InvestorProfile


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user with password confirmation.
    dj-rest-auth RegistrationView expects serializer.save(self.request)
    """

    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "user_phone",
            "password",
            "password2",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    # dj-rest-auth calls save(self, request)
    def save(self, request):  # type: ignore[override]
        data = dict(self.validated_data)
        data.pop("password2", None)

        user = UserProfile.objects.create_user(
            email=data["email"],
            username=data["username"],
            password=data["password"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            user_phone=data.get("user_phone"),
        )
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Custom password reset confirm via uid/token + new passwords.
    """

    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password1 = serializers.CharField(min_length=8, write_only=True)
    new_password2 = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        if attrs["new_password1"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password2": "Passwords do not match."})

        try:
            uid = force_str(urlsafe_base64_decode(attrs["uidb64"]))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exc:
            # W0707: chain original exception for better tracebacks
            raise serializers.ValidationError({"uidb64": "Invalid uid."}) from exc

        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        attrs["user"] = user
        return attrs

    def save(self, request=None, **kwargs):  # single save implementation (fixes E0102)
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password1"])
        user.save()
        return user


class CustomLoginSerializer(serializers.Serializer):
    """
    Serializer for user login with optional role verification.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=["startup", "investor"], required=False, allow_null=True
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        role = attrs.get("role")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if role == "startup" and not StartupProfile.objects.filter(user_id=user.id).exists():
            raise serializers.ValidationError("User is not a startup.")
        if role == "investor" and not InvestorProfile.objects.filter(user_id=user.id).exists():
            raise serializers.ValidationError("User is not an investor.")

        refresh = RefreshToken.for_user(user)
        refresh["email"] = user.email
        refresh["uid"] = user.id

        access = refresh.access_token
        access["email"] = user.email
        access["uid"] = user.id

        if role:
            refresh["role"] = role
            access["role"] = role

        return {"refresh": str(refresh), "access": str(access)}


class CustomPasswordResetConfirmSerializer(DJPasswordResetConfirmSerializer):
    """
    Extend dj-rest-auth PasswordResetConfirmSerializer to run Django validators.
    """

    def validate(self, attrs):
        attrs = super().validate(attrs)
        new_password = attrs.get("new_password1") or attrs.get("new_password")
        try:
            validate_password(new_password)
        except DjangoValidationError as exc:
            # keep original validation messages
            raise serializers.ValidationError({"new_password1": list(exc.messages)}) from exc
        return attrs
