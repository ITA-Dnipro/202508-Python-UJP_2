from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from profiles.models import InvestorProfile, Industry
from profiles.models import LOCATION_CHOICES
from users.models import UserProfile
from faker import Faker
import random

class Command(BaseCommand):
    '''Command to create fake investor profiles.'''
    help = "Fill the database with fake investor profile records."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=25, help="How many investor profiles to create.")
        parser.add_argument("--seed", type=int, default=12345, help="Random seed for deterministic data.")

    def handle(self, *args, **options):
        count = options["count"]
        seed = options["seed"]

        faker = Faker(["uk_UA"])
        faker.seed_instance(seed)
        random.seed(seed)

        InvestorProfile.objects.all().delete()
        created = 0
        faker.unique.clear()

        users = list(UserProfile.objects.all())
        if not users:
            self.stderr.write("No users found! Please create some users first.")
            return
        
        industries = list(Industry.objects.all())

        for _ in range(count):
            user_id=random.choice(users)
            investment_focus = random.choice(industries) if industries else ValueError("No industries found")
            location = random.choice([choice[0] for choice in LOCATION_CHOICES])
            created_at = make_aware(faker.date_time_this_decade())
            updated_at = make_aware(faker.date_time_between(start_date=created_at, end_date="now"))

            profile = InvestorProfile(
                user_id=user_id,
                investment_focus=investment_focus,
                location=location,
                created_at=created_at,
                updated_at=updated_at
            )

            try:
                profile.save()
                created += 1
            except Exception as exc:
                self.stderr.write(f"Skip investor profile due to error: {exc}")
                continue

        self.stdout.write(self.style.SUCCESS(f"Created {created} investor profiles"))
