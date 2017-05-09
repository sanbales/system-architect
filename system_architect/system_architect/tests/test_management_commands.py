from django.test import TestCase
from django.test.utils import override_settings
from system_architect.management.commands.add_fixture_data import Command


command = Command()


class ManagementCommandsTestCase(TestCase):
    def test_handle(self):
        command.handle(remake=True)

    @override_settings(DEBUG=True)
    def test_admin_user_creation(self):
        command.make_superuser()

    def test_naval(self):
        command.make_naval_example(project_name="Complex Test")

    def test_simple(self):
        command.make_simple_example(project_name="Simple Test")
