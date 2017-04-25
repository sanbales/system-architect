from csv import DictReader
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from os.path import abspath, dirname, join

from system_architect.models import (Category, Function, Scenario, System, WeightLevel, WeightingScale)


class Command(BaseCommand):
    help = 'Creates a superuser and other fixture data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Running add_fixture_data"))
        self.stdout.write(self.style.SUCCESS("  Creating Superuser:"))
        if settings.DEBUG:
            User.objects.create_superuser(settings.FIXTURE_SUPER_USERNAME, 'sanbales@gmail.com',
                                          settings.FIXTURE_SUPER_PASSWORD)
            self.stdout.write(self.style.SUCCESS("    - Created superuser (username: '{}', password: '{}')")
                              .format(settings.FIXTURE_SUPER_USERNAME, settings.FIXTURE_SUPER_PASSWORD))
        else:
            self.stdout.write(self.style.WARNING("    - Could not create superuser because settings.DEBUG is False"))

        path = dirname(abspath(__file__))

        with open(join(path, 'naval_systems.csv'), 'r') as csvfile:
            reader = DictReader(csvfile)
            systems = [System.objects.create(**row) for row in reader]
        self.stdout.write(self.style.SUCCESS("    - Created systems"))

        with open(join(path, 'naval_functions.csv'), 'r') as csvfile:
            reader = DictReader(csvfile)
            functions = [Function.objects.create(**row) for row in reader]
        self.stdout.write(self.style.SUCCESS("    - Created functions"))

        with open(join(path, 'naval_scenarios.csv'), 'r') as csvfile:
            reader = DictReader(csvfile)
            scenarios = [Scenario.objects.create(**row) for row in reader]
        self.stdout.write(self.style.SUCCESS("    - Created scenarios"))

        with open(join(path, 'naval_categories.csv'), 'r') as csvfile:
            reader = DictReader(csvfile)
            categories = [Category.objects.create(**row) for row in reader]
        self.stdout.write(self.style.SUCCESS("    - Created categories"))

        moscow = WeightingScale.objects.create(name='MoSCoW',
                                               description="A prioritization technique used in management.")
        moscow.add_level('Must Have', 1.0)
        moscow.add_level('Should Have', 0.8)
        moscow.add_level('Could Have', 0.4)
        moscow.add_level('Will Not Have', 0.0)

        likert = WeightingScale.objects.create(name='Likert',
                                               description="A prioritization technique used in management.")
        likert.add_level('Very Important', 1.0)
        likert.add_level('Important', 0.8)
        likert.add_level('Moderately Important', 0.5)
        likert.add_level('Of Little Importance', 0.25)
        likert.add_level('Unimportant', 0.0)

        qfd = WeightingScale.objects.create(name='House of Quality',
                                            description="A prioritization technique used in management.")
        qfd.add_level('High', 9.0)
        qfd.add_level('Medium', 3.0)
        qfd.add_level('Low', 1.0)
        qfd.add_level('N/A', 0.0)

        criticality = WeightingScale.objects.create(name='Criticality',
                                                    description="A measure of how critical one entity is to another.")
        criticality.add_level('Cannot Be Achieved Without', 1.0)
        criticality.add_level('Seriously Jeopardized Without', 0.8)
        criticality.add_level('Somewhat Jeopardized Without', 0.6)
        criticality.add_level('Minimally Jeopardized Without', 0.3)
        criticality.add_level('Practically Not Jeopardized Without', 0.1)
        criticality.add_level('Not Applicable', 0.0)
