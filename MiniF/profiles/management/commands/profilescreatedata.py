from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from profiles.models import StartupProfile
from users.models import UserProfile
from faker import Faker
import random

class Command(BaseCommand):
    help = "Fill the database with fake Profile records."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=25, help="How many profiles to create.")
        parser.add_argument("--seed", type=int, default=12345, help="Random seed for deterministic data.")

    def handle(self, *args, **options):
        count = options["count"]
        seed = options["seed"]

        faker = Faker(["uk_UA"])
        faker.seed_instance(seed)
        random.seed(seed)

        StartupProfile.objects.all().delete()
        created = 0
        faker.unique.clear()

        users = list(UserProfile.objects.all())
        if not users:
            self.stderr.write("No users found! Please create some users first.")
            return

        # industry = list(StartupProfile.objects.values_list('industry_id', flat=True).distinct())
        
        for _ in range(count):
            user_id=random.choice(users)
            company_name = faker.unique.company()
            description = faker.text(max_nb_chars=700)
            website = faker.url()
            industry_id = random.randint(1, 10)
            # industry_id = random.choice(industry) if industry else ValueError("No industry IDs found in existing profiles.")
            location = random.choice([choice[0] for choice in StartupProfile.LOCATION_CHOICES])
            created_at = make_aware(faker.date_time_this_decade())
            updated_at = make_aware(faker.date_time_between(start_date=created_at, end_date="now"))

            profile = StartupProfile(
                user_id=user_id,
                company_name=company_name,
                description=description,
                website=website,
                industry_id=industry_id,
                location=location,
                created_at=created_at,
                updated_at=updated_at
            )

            try:
                profile.save()
                created += 1
            except Exception as exc:
                self.stderr.write(f"Skip profile due to error: {exc}")
                continue

        self.stdout.write(self.style.SUCCESS(f"Created {created} profiles"))
