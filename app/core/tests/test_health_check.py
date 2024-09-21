"""
Tests for the health check endpoint.
"""

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

class HealthCheckTests(TestCase):
    """
    Tests for the health check endpoint.
    """
    def setUp(self):
        """
        Set up the test client.
        """
        self.client = APIClient()

    def test_health_check(self):
        """
        Test the health check endpoint.
        """
        url = reverse('health-check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)