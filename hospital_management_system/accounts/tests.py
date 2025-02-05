from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import User


# Create your tests here.
class AuthenticationTests(APITestCase):
    def test_register_user(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'role': 'PATIENT',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)