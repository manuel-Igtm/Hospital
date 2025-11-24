"""
Wait for database to be ready before starting Django.

This script attempts to connect to the database and retries until successful.
Useful for Docker Compose where Django might start before PostgreSQL is ready.
"""

import os
import sys
import time
from django.db import connections
from django.db.utils import OperationalError

def wait_for_db():
    """Wait for database to become available."""
    db_conn = connections['default']
    max_retries = 30
    retry_delay = 2
    
    print("🔄 Waiting for database...")
    
    for i in range(max_retries):
        try:
            db_conn.ensure_connection()
            print("✅ Database is ready!")
            return True
        except OperationalError as e:
            if i < max_retries - 1:
                print(f"⏳ Database unavailable, waiting {retry_delay}s... (attempt {i+1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print(f"❌ Database not available after {max_retries} attempts")
                print(f"Error: {e}")
                return False
    
    return False

if __name__ == '__main__':
    # Django setup
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
    import django
    django.setup()
    
    # Wait for DB
    if not wait_for_db():
        sys.exit(1)
