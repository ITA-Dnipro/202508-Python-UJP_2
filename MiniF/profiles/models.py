from django.db import models
from django.utils import timezone

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
    ("Zhytomyr", "Zhytomyr"),
]


class Industry(models.Model):
    """
    Industry model.
    """

    industry_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.industry_name


class StartupProfile(models.Model):
    user_id = models.ForeignKey(
        "users.UserProfile",
        on_delete=models.CASCADE,
        related_name="startup_profiles",
    )
    company_name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    website = models.URLField(blank=True, null=True)
    industry_id = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name="startups")
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["industry_id"]),
            models.Index(fields=["location"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["user_id"], name="uniq_startup_per_user"),
        ]

    def __str__(self):
        return self.company_name


class InvestorProfile(models.Model):
    user_id = models.ForeignKey(
        "users.UserProfile",
        on_delete=models.CASCADE,
        related_name="investor_profiles",
    )
    investment_focus = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name="investors")
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["investment_focus"]),
            models.Index(fields=["location"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["user_id"], name="uniq_investor_per_user"),
        ]

    def __str__(self):
        return f"Investor: {self.user_id.email} (focus: {self.investment_focus})"
