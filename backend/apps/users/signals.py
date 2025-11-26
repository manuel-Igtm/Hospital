"""
Signal handlers for the users app.

Copyright (c) 2025, Immanuel Njogu. All rights reserved.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

# Signal handlers can be added here as needed
# Example:
# @receiver(post_save, sender=User)
# def user_created(sender, instance, created, **kwargs):
#     if created:
#         # Handle new user creation
#         pass
