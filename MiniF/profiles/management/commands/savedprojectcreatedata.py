from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from profiles.models import StartupProfile, InvestorProfile, SavedProject
from projects.models import StartupProject
from users.models import UserProfile
from faker import Faker
import random

class Command(BaseCommand):
    '''Command to create fake saved projects profiles.'''
    help = "Fill the database with fake saved projects profiles."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=25, help="How many saved projects to create.")
        parser.add_argument("--seed", type=int, default=12345, help="Random seed for deterministic data.")

    def handle(self, *args, **options):
        count = options["count"]
        seed = options["seed"]

        faker = Faker(["uk_UA"])
        faker.seed_instance(seed)
        random.seed(seed)

        SavedProject.objects.all().delete()
        created = 0
        faker.unique.clear()

        investorprofile = list(InvestorProfile.objects.all())
        if not investorprofile:
            self.stderr.write("No investor profiles found! Please create some profiles first.")
            return

        startupproject = list(StartupProject.objects.all())
        if not startupproject:
            self.stderr.write("No startup projects found! Please create some projects first.")
            return

        for _ in range(count):

            investor = random.choice(investorprofile)
            project = random.choice(startupproject)
            created_at = make_aware(faker.date_time_this_decade())

            saved_project = SavedProject(
                investor=investor,
                project=project,
                created_at=created_at
            )

            try:
                saved_project.save()
                created += 1
            except Exception as exc:
                self.stderr.write(f"Skip profile due to error: {exc}")
                continue

        self.stdout.write(self.style.SUCCESS(f"Created {created} saved project profiles"))