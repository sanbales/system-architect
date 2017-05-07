from csv import DictReader
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from os.path import abspath, dirname, join

from system_architect.models import Category, Function, Project, Scenario, System, WeightingScale


class Command(BaseCommand):
    help = 'Creates a superuser and other fixture data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Running add_fixture_data"))
        self.make_superuser()
        self.make_simple_example(force=options['force'])
        self.make_naval_example(force=options['force'])

    def make_superuser(self):
        self.stdout.write(self.style.SUCCESS("  Creating Superuser:"))
        if settings.DEBUG:
            User.objects.create_superuser(settings.FIXTURE_SUPER_USERNAME, 'sanbales@gmail.com',
                                          settings.FIXTURE_SUPER_PASSWORD)
            self.stdout.write(self.style.SUCCESS("    - Created superuser (username: '{}', password: '{}')")
                              .format(settings.FIXTURE_SUPER_USERNAME, settings.FIXTURE_SUPER_PASSWORD))
        else:
            self.stdout.write(self.style.WARNING("    - Could not create superuser because settings.DEBUG is False"))

    def make_simple_example(self, project_name="Make Toasts Great Again", force=False):
        self.stdout.write(self.style.SUCCESS("  Creating '{}' Example".format(project_name)))

        if Project.objects.filter(name=project_name).count() > 0:
            if force:
                Project.objects.filter(name=project_name).delete()
            else:
                return

        project = Project.objects.create(name=project_name,
                                         description="An simple example to test the framework.")
        self.stdout.write(self.style.SUCCESS("    - Created project"))
        goal = project.add_goal(name='Better Toasting', description='Make better toast, faster and more easily.')
        self.stdout.write(self.style.SUCCESS("    - Created goal"))
        better = project.add_function(name='Better toasts',
                                      description='Make better tasting and looking toasts out of any bread')
        faster = project.add_function(name='Faster toasts',
                                      description='Make toasts in less time and with less variability in duration')
        easier = project.add_function(name='Easier toasts', description='Make it easier to get toast golden brown')

        self.stdout.write(self.style.SUCCESS("    - Created high level functions"))

        # Better
        golden = project.add_function(name='Unburnt toasts', description='Make toasts be golden brown')
        robust = project.add_function(name='Toast robustly', description='Make toasting insensitive to type of bread,' +
                                                                         ' thickness, or temperature')
        better.requires.add(golden, robust)
        better.save()

        # Easier
        more = project.add_function(name='More toast',
                                    description='Allow for more than 2 toasts to be made at the same time')
        no_guess = project.add_function(name='Less guessing',
                                        description='Require less guessing from the user for toaster inputs')
        easier.required.add(more, no_guess)
        easier.save()
        self.stdout.write(self.style.SUCCESS("    - Created remaining functions"))

        self.stdout.write(self.style.SUCCESS("    - Finish creating fixture data for '{}'".format(project_name)))

    def make_naval_example(self, project_name="Naval Example", folder='naval_example', force=False):

        if Project.objects.filter(name=project_name).count() > 0:
            if force:
                Project.objects.filter(name=project_name).delete()
            else:
                return

        path = dirname(abspath(__file__))

        project = Project.objects.create(name=project_name,
                                         description="An example of a naval system architecting problem.")

        with open(join(path, folder, 'naval_systems.csv'), 'r') as csvfile:
            reader = DictReader(csvfile)
            systems = [System.objects.create(project=project, **row) for row in reader]
        self.stdout.write(self.style.SUCCESS("    - Created systems"))

        with open(join(path, folder, 'naval_functions.csv'), 'r') as csvfile:
            reader = DictReader(csvfile)
            functions = [Function.objects.create(project=project, **row) for row in reader]
        self.stdout.write(self.style.SUCCESS("    - Created functions"))

        with open(join(path, folder, 'naval_scenarios.csv'), 'r') as csvfile:
            reader = DictReader(csvfile)
            scenarios = {}
            for row in reader:
                parent = row.pop('parent', None)
                if parent in scenarios:
                    parent = scenarios[parent]
                elif not parent:
                    parent = None
                else:
                    self.stderr.write(self.style.ERROR("      - Could not find '{}' in scenarios".format(parent)))

                scenarios[row['name']] = Scenario.objects.create(project=project, parent=parent, **row)
        self.stdout.write(self.style.SUCCESS("    - Created scenarios"))

        with open(join(path, folder, 'naval_categories.csv'), 'r') as csvfile:
            reader = DictReader(csvfile)
            categories = [Category.objects.create(project=project, **row) for row in reader]
        self.stdout.write(self.style.SUCCESS("    - Created categories"))

        moscow = project.add_scale(name='MoSCoW',
                                   description="A prioritization technique used in management.")
        moscow.add_level('Must Have', 1.0)
        moscow.add_level('Should Have', 0.8)
        moscow.add_level('Could Have', 0.4)
        moscow.add_level('Will Not Have', 0.0)

        likert = project.add_scale(name='Likert',
                                   description="A prioritization technique used in management.")
        likert.add_level('Very Important', 1.0)
        likert.add_level('Important', 0.8)
        likert.add_level('Moderately Important', 0.5)
        likert.add_level('Of Little Importance', 0.25)
        likert.add_level('Unimportant', 0.0)

        qfd = project.add_scale(name='House of Quality', description="A prioritization technique used in management.")
        qfd.add_level('High', 9.0)
        qfd.add_level('Medium', 3.0)
        qfd.add_level('Low', 1.0)
        qfd.add_level('N/A', 0.0)

        criticality = project.add_scale(name='Criticality',
                                        description="A measure of how critical one entity is to another.")
        criticality.add_level('Cannot Be Achieved Without', 1.0)
        criticality.add_level('Seriously Jeopardized Without', 0.8)
        criticality.add_level('Somewhat Jeopardized Without', 0.6)
        criticality.add_level('Minimally Jeopardized Without', 0.3)
        criticality.add_level('Practically Not Jeopardized Without', 0.1)
        criticality.add_level('Not Applicable', 0.0)

        satisfiability = project.add_scale(name='Satisfiability',
                                           description="A measure of how well something can satisfy something else.")
        satisfiability.add_level('Completely satisfies the function under all circumstances', 1.0)
        satisfiability.add_level('Satisfies the function under most circumstances', 0.8)
        satisfiability.add_level('Satisfies the function under some circumstances', 0.2)
        satisfiability.add_level('Does not satisfies the function', 0.0)
