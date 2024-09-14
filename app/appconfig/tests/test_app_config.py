from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import AppConfiguration, User

class AppConfigurationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse('app-configuration-list-create')
        self.active_url = reverse('active-app-configuration')
        self.user = User.objects.create_user(email='user@example.com', password='testpass123')
        self.staff_user = User.objects.create_user(email='staff@example.com', password='testpass123', is_staff=True)
        self.superuser = User.objects.create_superuser(email='admin@example.com', password='testpass123')

    def test_create_app_configuration_unauthorized(self):
        self.client.force_authenticate(user=self.user)
        payload = {'version': '1.0', 'configurations': {'key': 'value'}}
        res = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_app_configuration_staff(self):
        self.client.force_authenticate(user=self.staff_user)
        payload = {'version': '1.0', 'configurations': {'key': 'value'}}
        res = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_app_configuration_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        payload = {'version': '1.0', 'configurations': {'key': 'value'}}
        res = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_app_configurations(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_active_configuration(self):
        AppConfiguration.objects.create(version='1.0', is_active=True, configurations={'key': 'value'})
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.active_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['version'], '1.0')

    def test_create_multiple_active_configurations(self):
        self.client.force_authenticate(user=self.staff_user)
        payload1 = {'version': '1.0', 'is_active': True, 'configurations': {'key': 'value1'}}
        payload2 = {'version': '2.0', 'is_active': True, 'configurations': {'key': 'value2'}}
        self.client.post(self.list_url, payload1, format='json')
        res = self.client.post(self.list_url, payload2, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        active_configs = AppConfiguration.objects.filter(is_active=True)
        self.assertEqual(active_configs.count(), 1)
        self.assertEqual(active_configs.first().version, '2.0')
