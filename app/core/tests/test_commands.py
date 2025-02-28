"""Test custom Django management commands."""
from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase

# Import MySQLdb OperationalError properly
try:
    from MySQLdb import OperationalError as MySQLOpError
except ImportError:
    # Fallback for when MySQLdb is not installed
    MySQLOpError = OperationalError


class CommandTests(SimpleTestCase):
    """Test commands for waiting for the database."""

    @patch('django.db.connection.ensure_connection')
    def test_wait_for_db_ready(self, patched_ensure_connection):
        """Test that the wait_for_db command proceeds
        if the database is ready."""
        # Set up the mock to return immediately
        patched_ensure_connection.return_value = None

        call_command('wait_for_db')

        patched_ensure_connection.assert_called_once()

    @patch('time.sleep')
    @patch('django.db.connection.ensure_connection')
    def test_wait_for_db_delay(self, patched_ensure_connection, patched_sleep):
        """Test wait_for_db retries on database connection errors."""
        # Set up side effects - first 5 calls raise error, 6th succeeds
        patched_ensure_connection.side_effect = [OperationalError] * 2 + \
            [MySQLOpError] * 3 + [None]

        call_command('wait_for_db')

        self.assertEqual(patched_ensure_connection.call_count, 6)
