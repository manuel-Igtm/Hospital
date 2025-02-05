from django.db import models
from accounts.models import User

# Create your models here.
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor',unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15,)
    address = models.TextField()

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}"