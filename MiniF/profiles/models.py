from django.db import models
from django.utils import timezone
from projects.models import StartupProject


class Industry(models.Model):
    industry_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.industry_name


class StartupProfile(models.Model):
    """
    Startup profile model.

    Notes:
    - Set the website field as URLField.
    """

    user_id = models.ForeignKey("users.UserProfile", on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    website = models.URLField(blank=True, null=True)
    industry_id = models.ForeignKey(Industry, on_delete=models.CASCADE)
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
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["industry_id"]),
            models.Index(fields=["location"]),
        ]

    def __str__(self):
        return self.company_name


class InvestorProfile(models.Model):
    """
    Investor profile model.
    """

    user_id = models.ForeignKey("users.UserProfile", on_delete=models.CASCADE)
    investment_focus = models.ForeignKey(Industry, on_delete=models.CASCADE)
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
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    # def __str__(self):
    #     return self.company_name


class SavedProject(models.Model):
    """
    Model for investor's saved startup projects.
    """

    investor = models.ForeignKey("profiles.InvestorProfile", on_delete=models.CASCADE)
    project = models.ForeignKey(StartupProject, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["investor", "project"], name="unique_investor_project")]

    def __str__(self):
        return f"{self.investor} liked {self.project}"
