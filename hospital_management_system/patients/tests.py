from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Patient
from accounts.models import User

# Create your tests here.

class PatientTests(APITestCase):
    def setUp(self):
        # Create a new user for testing
        self.user = User.objects.create_user(
            username='testpatient',
            password='testpass123',
            role='PATIENT'
        )

    def test_create_patient(self):
        url = reverse('patient-list')
        data = {
            'user': self.user.id,  # Use the ID of the newly created user
            'first_name': 'Jane',
            'last_name': 'Doe',
            'date_of_birth': '1995-05-05',
            'contact_number': '0987654321',
            'address': '456 Elm St',
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 201)  # Expect 201 Created