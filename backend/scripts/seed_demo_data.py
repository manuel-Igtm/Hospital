#!/usr/bin/env python
"""
Seed script for demo data.

Creates demo users with different roles for testing and development.

Usage:
    python manage.py shell < scripts/seed_demo_data.py

    Or run directly:
    cd backend && python scripts/seed_demo_data.py

© 2025 Immanuel Njogu. All rights reserved.
"""

import os
import sys
from pathlib import Path

# Add backend to path if running directly
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

import django

django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

# Demo users configuration
DEMO_USERS = [
    {
        "email": "admin@hospital.local",
        "password": "admin123!",
        "first_name": "System",
        "last_name": "Administrator",
        "role": "admin",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "email": "dr.smith@hospital.local",
        "password": "doctor123!",
        "first_name": "John",
        "last_name": "Smith",
        "role": "doctor",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "nurse.jane@hospital.local",
        "password": "nurse123!",
        "first_name": "Jane",
        "last_name": "Doe",
        "role": "nurse",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "lab.tech@hospital.local",
        "password": "lab123!",
        "first_name": "Mike",
        "last_name": "Johnson",
        "role": "lab_technician",
        "is_staff": False,
        "is_superuser": False,
    },
]


def create_demo_users() -> None:
    """Create demo users if they don't exist."""
    print("Creating demo users...")

    created_count = 0
    skipped_count = 0

    with transaction.atomic():
        for user_data in DEMO_USERS:
            email = user_data["email"]
            password = user_data.pop("password")

            user, created = User.objects.get_or_create(
                email=email,
                defaults=user_data,
            )

            if created:
                user.set_password(password)
                user.save()
                print(f"  ✓ Created: {email} ({user_data['role']})")
                created_count += 1
            else:
                print(f"  - Skipped (exists): {email}")
                skipped_count += 1

    print(f"\nSummary: {created_count} created, {skipped_count} skipped")


def print_credentials() -> None:
    """Print demo user credentials."""
    print("\n" + "=" * 60)
    print("Demo User Credentials")
    print("=" * 60)
    print(f"{'Email':<30} {'Password':<15} {'Role':<15}")
    print("-" * 60)
    for user in DEMO_USERS:
        print(f"{user['email']:<30} {user.get('password', 'N/A'):<15} {user['role']:<15}")
    print("=" * 60)
    print("\nWARNING: These are demo credentials. Do NOT use in production!")


if __name__ == "__main__":
    # Re-add passwords for credential display (they were popped during creation)
    DEMO_USERS[0]["password"] = "admin123!"
    DEMO_USERS[1]["password"] = "doctor123!"
    DEMO_USERS[2]["password"] = "nurse123!"
    DEMO_USERS[3]["password"] = "lab123!"

    print_credentials()
    print()
    create_demo_users()
