from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from dj_rest_auth.serializers import LoginSerializer
from profiles.models import StartupProfile, InvestorProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ["email", "username", "first_name", "last_name", "user_phone", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        return UserProfile.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            user_phone=validated_data.get("user_phone"),
        )

    def save(self, request=None):
        return super().save()


class CustomLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=["startup", "investor"])

    def validate(self, data):
        email = data["email"]
        password = data["password"]
        role = data["role"]

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        refresh = RefreshToken.for_user(user)

        refresh["role"] = role
        refresh["email"] = user.email
        refresh["uid"] = user.id
        access = refresh.access_token
        access["role"] = role
        access["email"] = user.email
        access["uid"] = user.id

        return {
            "refresh": str(refresh),
            "access": str(access),
        }
