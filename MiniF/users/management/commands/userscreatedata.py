from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from django.contrib.auth import get_user_model
from faker import Faker

import random

class Command(BaseCommand):
    help = "Fill the database with fake UserProfile records."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=50, help="How many users to create.")
        parser.add_argument("--seed", type=int, default=12345, help="Random seed for deterministic data.")
        parser.add_argument("--password", type=str, default="Password123!", help="Password for created users.")

    def handle(self, *args, **options):
        count = options["count"]
        seed = options["seed"]
        password = options["password"]

        faker = Faker(["uk_UA"])
        faker.seed_instance(seed)
        random.seed(seed)

        User = get_user_model()
        User.objects.exclude(is_superuser=True).delete()

        created = 0
        faker.unique.clear()

        for _ in range(count):
            first_name = faker.first_name()
            last_name = faker.last_name()
            email = faker.unique.email()
            username = faker.unique.user_name()
            user_phone = "380" + str(faker.random_number(digits=9, fix_len=True))
            date_joined = make_aware(faker.date_time_this_decade())
            updated_at = make_aware(faker.date_time_between(start_date=date_joined))

            user = User(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                user_phone=user_phone,
                date_joined=date_joined,
                updated_at=updated_at
            )
            user.set_password(password)
            user.save()

            try:
                user.save()
                created += 1
            except Exception as exc:
                self.stderr.write(f"Skip user due to error: {exc}")
                continue

        self.stdout.write(self.style.SUCCESS(f"Created {created} users"))