from django.test import TestCase

from system_architect.management.commands.add_fixture_data import Command
from system_architect.models import (Function, Project, System)


command = Command()


class AppTestCase(TestCase):
    def setUp(self):
        command.handle()

    def test_project(self):
        self.assertEqual(Project.objects.count(), 1)

    # TODO: complete the tests for all the models
