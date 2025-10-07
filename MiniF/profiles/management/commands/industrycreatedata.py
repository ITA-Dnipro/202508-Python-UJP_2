from django.core.management.base import BaseCommand
from profiles.models import Industry
from faker import Faker
import random

class Command(BaseCommand):
    '''Command to create fake industry records.'''
    help = "Fill the database with fake Profile records."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=25, help="How many industries to create.")
        parser.add_argument("--seed", type=int, default=12345, help="Random seed for deterministic data.")

    def handle(self, *args, **options):
        count = options["count"]
        seed = options["seed"]

        faker = Faker(["uk_UA"])
        faker.seed_instance(seed)
        random.seed(seed)

        Industry.objects.all().delete()
        created = 0

        for _ in range(count):
            industry_name = faker.word().capitalize() + " " + faker.word().capitalize()
            industry = Industry(industry_name=industry_name)
            try:
                industry.save()
                created += 1
            except Exception as exc:
                self.stderr.write(f"Skip industry due to error: {exc}")
                continue

        self.stdout.write(self.style.SUCCESS(f"Created {created} industries"))
