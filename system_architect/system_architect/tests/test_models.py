from django.test import TestCase

from system_architect.management.commands.add_fixture_data import Command
from system_architect.models import (Function, Project, System)


command = Command()


class SystemArchitectTestCase(TestCase):
    def setUp(self):
        command.make_simple_example(project_name="Simple Test Case")

    def test_project(self):
        self.assertEqual(Project.objects
                                .filter(name="Simple Test Case")
                                .count(), 1)

    # TODO: complete the tests for all the models
