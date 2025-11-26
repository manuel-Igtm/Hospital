"""
Django management command: wait for database to be ready.
Usage: python manage.py wait_for_db
"""

import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to wait for database."""

    help = "Wait for database to become available"

    def add_arguments(self, parser):
        parser.add_argument("--max-retries", type=int, default=30, help="Maximum number of connection attempts")
        parser.add_argument("--retry-delay", type=int, default=2, help="Seconds to wait between retries")

    def handle(self, *args, **options):
        max_retries = options["max_retries"]
        retry_delay = options["retry_delay"]

        self.stdout.write("🔄 Waiting for database...")

        for i in range(max_retries):
            try:
                db_conn = connections["default"]
                db_conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS("✅ Database is ready!"))
                return
            except OperationalError:
                if i < max_retries - 1:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⏳ Database unavailable, waiting {retry_delay}s... " f"(attempt {i+1}/{max_retries})"
                        )
                    )
                    time.sleep(retry_delay)
                else:
                    self.stdout.write(self.style.ERROR(f"❌ Database not available after {max_retries} attempts"))
                    raise
