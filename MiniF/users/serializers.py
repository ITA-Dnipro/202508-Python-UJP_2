from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
from profiles.models import StartupProfile, InvestorProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user with password confirmation.
    """

    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ["email", "username", "first_name", "last_name", "user_phone", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        """
        Ensure both password fields match.
        """
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        """
        Create a new user with the provided data.
        """
        validated_data.pop("password2")
        return UserProfile.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            user_phone=validated_data.get("user_phone"),
        )

    def save(self, request=None, *args, **kwargs):
        """
        Swallow the positional 'request' passed by dj-rest-auth and delegate to the parent.
        """
        return super().save(**kwargs)


class CustomLoginSerializer(serializers.Serializer):
    """
    Serializer for user login with optional role verification.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=["startup", "investor"], required=False, allow_null=True)

    def validate(self, attrs):
        """
        Validate user credentials and generate JWT tokens.
        Optionally ensure the user has the requested role.
        """
        email = attrs.get("email")
        password = attrs.get("password")
        role = attrs.get("role")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if role == "startup" and not StartupProfile.objects.filter(user_id=user).exists():
            raise serializers.ValidationError("User is not a startup.")
        if role == "investor" and not InvestorProfile.objects.filter(user_id=user).exists():
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
