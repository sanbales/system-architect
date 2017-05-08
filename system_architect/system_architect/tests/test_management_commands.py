from django.test import TestCase

from system_architect.management.commands.add_fixture_data import Command
from system_architect.models import (Function, Project, System)


command = Command()


class ManagementCommandsTestCase(TestCase):
    def test_naval(self):
        command.make_naval_example(project_name="Complex Test")

    def test_simple(self):
        command.make_simple_example(project_name="Simple Test")
