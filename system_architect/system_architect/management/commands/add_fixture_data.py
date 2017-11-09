#!/usr/bin/env python
# -*- coding: utf-8 -*-
from csv import DictReader
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from os.path import abspath, dirname, join

from system_architect.models import Category, Function, FunctionRequires, Project, Scenario, System


class Command(BaseCommand):
    """Management Commands for the Django System Architecting app."""

    help = 'Creates a superuser and other fixture data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--remake',
            action='store_true',
            dest='remake',
            default=False,
            help='Delete old fixture data if it exists',
        )

    def handle(self, *args, **options):
        self.stdout.write("Running add_fixture_data")
        self.make_superuser()
        self.make_simple_example(remake=options['remake'])
        self.make_naval_example(remake=options['remake'])

    def make_superuser(self):
        self.stdout.write("  Creating Superuser:")
        username = settings.FIXTURE_SUPER_USERNAME
        email = settings.FIXTURE_USER_EMAIL
        password = settings.FIXTURE_SUPER_PASSWORD
        if settings.DEBUG:
            User.objects.create_superuser(username, email, password)
            msg = "    - Created superuser (username: '{}', password: '{}')"
            self.stdout.write(msg.format(username, password))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "    - Could not create superuser because settings.DEBUG is False"))

    def make_simple_example(self, project_name="Make Toasts Great Again", remake=False):
        """Create fixture data for a simple yet easy to understand example."""
        self.stdout.write(
            "  Creating '{}' Example".format(project_name))

        if Project.objects.filter(name=project_name).count() > 0:
            if remake:
                Project.objects.filter(name=project_name).delete()
            else:
                return

        project = Project.objects.create(
            name=project_name,
            description="An simple example to test the framework.",
        )
        self.stdout.write("    - Created project")
        goal = project.add_goal(
            name='Better Toasting',
            description='Make better toast, faster and more easily.',
        )
        self.stdout.write("    - Created goal")
        better = project.add_function(
            name='Better toasts',
            description='Make better tasting and looking toasts out of any bread',
        )
        faster = project.add_function(
            name='Faster toasts',
            description='Make toasts in less time and with less variability in duration',
        )
        easier = project.add_function(
            name='Easier toasts',
            description='Make it easier to get toast golden brown',
        )

        criticality = self.make_criticality_scale(project)
        satisfiability = self.make_satisfiability_scale(project)

        self.stdout.write(
            "    - Created high level functions")

        # Better
        golden = project.add_function(
            name='Unburnt toasts',
            description='Make toasts be golden brown',
        )
        robust = project.add_function(
            name='Toast robustly',
            description='Make toasting insensitive to type of bread,' +
                        ' thickness, or temperature')
        for required in (golden, robust):
            FunctionRequires.objects.create(
                requiring=better,
                required=required,
                project=project,
                scale=criticality,
            )

        # Easier
        more = project.add_function(
            name='More toast',
            description='Allow for more than 2 toasts to be made at the same time',
        )
        no_guess = project.add_function(
            name='Less guessing',
            description='Require less guessing from the user for toaster inputs',
        )
        for required in (more, no_guess):
            FunctionRequires.objects.create(
                requiring=easier,
                required=required,
                project=project,
                scale=criticality,
            )
        self.stdout.write("    - Created remaining functions")

        # TODO: finish making this example
        msg = "    - Finished creating fixture data for '{}'"
        self.stdout.write(msg.format(project_name))

    def make_naval_example(self, project_name="Naval Example",
                           folder='naval_example',
                           remake=False):
        """Make fixture data for a notional non-trivial architecting problem."""

        if Project.objects.filter(name=project_name).count() > 0:
            if remake:
                Project.objects.filter(name=project_name).delete()
            else:
                return
        self.stdout.write("  Creating Fixture Data for '{}'".format(project_name))

        path = dirname(abspath(__file__))

        project = Project.objects.create(name=project_name,
                                         description="An example of a naval system architecting problem.")

        with open(join(path, folder, 'naval_systems.csv'), 'r') as csvfile:
            reader = DictReader(csvfile)
            systems = [System.objects.create(project=project, **row) for row in reader]

        self.stdout.write("    - Created systems")

        with open(join(path, folder, 'naval_functions.csv'), 'r') as csvfile:
            reader = DictReader(csvfile)
            functions = [Function.objects.create(project=project, **row) for row in reader]

        self.stdout.write("    - Created functions")

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

        self.stdout.write("    - Created scenarios")

        with open(join(path, folder, 'naval_categories.csv'), 'r') as csvfile:
            reader = DictReader(csvfile)
            categories = [Category.objects.create(project=project, **row) for row in reader]

        self.stdout.write("    - Created categories")

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

        qfd = project.add_scale(name='House of Quality',
                                description="A prioritization technique used in management.")
        qfd.add_level('High', 9.0)
        qfd.add_level('Medium', 3.0)
        qfd.add_level('Low', 1.0)
        qfd.add_level('N/A', 0.0)

        criticality = self.make_criticality_scale(project)

        satisfiability = self.make_satisfiability_scale(project)

        self.stdout.write("    - Created scales")

        self.stdout.write("    - Finished creating fixture data for '{}'".format(project_name))

    @staticmethod
    def make_criticality_scale(project):
        criticality = project.add_scale(name='Criticality',
                                        description="A measure of how critical one entity is to another.")
        criticality.add_level('Cannot Be Achieved Without', 1.0)
        criticality.add_level('Seriously Jeopardized Without', 0.8)
        criticality.add_level('Somewhat Jeopardized Without', 0.6)
        criticality.add_level('Minimally Jeopardized Without', 0.3)
        criticality.add_level('Practically Not Jeopardized Without', 0.1)
        criticality.add_level('Not Applicable', 0.0)
        return criticality

    @staticmethod
    def make_satisfiability_scale(project):
        satisfiability = project.add_scale(name='Satisfiability',
                                           description="A measure of how well something can satisfy something else.")
        satisfiability.add_level('Completely satisfies the function under all circumstances', 1.0)
        satisfiability.add_level('Satisfies the function under most circumstances', 0.8)
        satisfiability.add_level('Satisfies the function under some circumstances', 0.2)
        satisfiability.add_level('Does not satisfies the function', 0.0)
        return satisfiability
