from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Doctor
from accounts.models import User


# Create your tests here.
from django.urls import reverse
from rest_framework.test import APITestCase
from accounts.models import User
from doctors.models import Doctor

class DoctorTests(APITestCase):
    def setUp(self):
        # Create a new user for testing
        self.user = User.objects.create_user(
            username='testdoctor',
            password='testpass123',
            role='DOCTOR'
        )

    def test_create_doctor(self):
        url = reverse('doctor-list')
        data = {
            'user': self.user.id,  # Use the ID of the newly created user
            'first_name': 'John',
            'last_name': 'Doe',
            'specialization': 'Cardiology',
            'contact_number': '1234567890',
            'address': '123 Main St',
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 201)  # Expect 201 Created