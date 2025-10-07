from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from profiles.models import StartupProfile
from projects.models import StartupProject
from faker import Faker
import random

class Command(BaseCommand):
    '''Command to create fake startup projects.'''
    help = "Fill the database with fake startup project records."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=25, help="How many projects to create.")
        parser.add_argument("--seed", type=int, default=12345, help="Random seed for deterministic data.")

    def handle(self, *args, **options):
        count = options["count"]
        seed = options["seed"]

        faker = Faker(["uk_UA"])
        faker.seed_instance(seed)
        random.seed(seed)

        StartupProject.objects.all().delete()
        created = 0
        faker.unique.clear()

        startupprofiles = list(StartupProfile.objects.all())
        if not startupprofiles:
            self.stderr.write("No startup profiles found! Please create some profiles first.")
            return

        for _ in range(count):
            startup_profile = random.choice(startupprofiles)
            title = faker.sentence(nb_words=4)
            likes = faker.random_number(digits=1, fix_len=False)
            description = " ".join(faker.words(nb=50))
            status = random.choice(["Planning", "In Progress", "Completed", "On Hold"])
            created_at = make_aware(faker.date_time_this_decade())
            updated_at = make_aware(faker.date_time_between(start_date=created_at, end_date="now"))

            project = StartupProject(
                startup_profile_id=startup_profile,
                title=title,
                likes=likes,
                description=description,
                status=status,
                created_at=created_at,
                updated_at=updated_at
            )

            try:
                project.save()
                created += 1
            except Exception as exc:
                self.stderr.write(f"Skip project due to error: {exc}")
                continue

        self.stdout.write(self.style.SUCCESS(f"Created {created} startup projects"))
