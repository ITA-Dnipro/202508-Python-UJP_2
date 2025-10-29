from django.contrib.auth import get_user_model
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
     Adapter that links a social account (Google)
     to an existing user via email
    """

    def pre_social_login(self, request, sociallogin):
        if request.user.is_authenticated:
            return

        email = sociallogin.account.extra_data.get("email")
        if not email:
            return

        try:
            user = User.objects.get(email=email)

            sociallogin.connect(request, user)

            EmailAddress.objects.update_or_create(
                user=user,
                email=email,
                defaults={"verified": True, "primary": True},
            )

        except User.DoesNotExist:
            pass
