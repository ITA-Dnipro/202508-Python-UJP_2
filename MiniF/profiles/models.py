from django.db import models
from django.utils import timezone
from users.models import UserProfile


class StartupProfile(models.Model):
    """
    Startup profile model.

    Notes:
    - Set the website field as URLField.
    """
    user_id = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    website = models.URLField(blank=True, null=True)
    industry_id =models.IntegerField()
    LOCATION_CHOICES = [
        ("Cherkasy", "Cherkasy"),
        ("Chernihiv", "Chernihiv"),
        ("Chernivtsi", "Chernivtsi"),
        ("Crimea", "Crimea"),
        ("Dnipro", "Dnipro"),
        ("Donetsk", "Donetsk"),
        ("Ivano-Frankivsk", "Ivano-Frankivsk"),
        ("Kharkiv", "Kharkiv"),
        ("Kherson", "Kherson"),
        ("Khmelnytskyi", "Khmelnytskyi"),
        ("Kirovohrad", "Kirovohrad"),
        ("Kyiv", "Kyiv"),
        ("Luhansk", "Luhansk"),
        ("Lviv", "Lviv"),
        ("Mykolaiv", "Mykolaiv"),
        ("Odesa", "Odesa"),
        ("Poltava", "Poltava"),
        ("Rivne", "Rivne"),
        ("Sumy", "Sumy"),
        ("Ternopil", "Ternopil"),
        ("Vinnytsia", "Vinnytsia"),
        ("Volyn", "Volyn"),
        ("Zakarpattia", "Zakarpattia"),
        ("Zaporizhzhia", "Zaporizhzhia"),
        ("Zhytomyr", "Zhytomyr"),]
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)

class InvestorProfile(UserProfile):
    class Meta:
        proxy = True
        app_label = "profiles"  # щоб було в цьому ж додатку
        verbose_name = "Investor Profile"
        verbose_name_plural = "Investor Profiles"

    def is_investor(self):
        return True