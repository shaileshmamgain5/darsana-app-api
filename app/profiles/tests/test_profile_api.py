from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Profile, JournalTemplate
from datetime import datetime, time

PROFILE_URL = reverse('profile')

class PublicProfileApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateProfileApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.profile = Profile.objects.create(user=self.user)

    def test_retrieve_profile(self):
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], self.user.email)

    def test_update_profile(self):
        payload = {
            'name': 'New Name',
            'theme': 'dark',
            'day_start': '07:00:00',
            'day_end': '22:00:00',
            'week_start': 'monday',
            'model_imagination': 'high'
        }
        res = self.client.patch(PROFILE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        for key, value in payload.items():
            if key in ['day_start', 'day_end']:
                self.assertEqual(getattr(self.profile, key), datetime.strptime(value, '%H:%M:%S').time())
            else:
                self.assertEqual(getattr(self.profile, key), value)

    def test_update_user_email_not_allowed(self):
        payload = {'email': 'newemail@example.com'}
        res = self.client.patch(PROFILE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, payload['email'])

    def test_update_morning_intention(self):
        journal_template = JournalTemplate.objects.create(
            title='Morning Intention',
            user=self.user
        )
        payload = {'morning_intention_id': journal_template.id}
        res = self.client.patch(PROFILE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.morning_intention.id, journal_template.id)

    def test_update_evening_reflection(self):
        journal_template = JournalTemplate.objects.create(
            title='Evening Reflection',
            user=self.user
        )
        payload = {'evening_reflection_id': journal_template.id}
        res = self.client.patch(PROFILE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.evening_reflection.id, journal_template.id)

    def test_partial_update_profile(self):
        original_week_start = self.profile.week_start
        payload = {'theme': 'dark'}
        res = self.client.patch(PROFILE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.theme, payload['theme'])
        self.assertEqual(self.profile.week_start, original_week_start)

    def test_full_update_profile(self):
        payload = {
            'name': 'Full Update',
            'theme': 'light',
            'day_start': '06:00:00',
            'day_end': '23:00:00',
            'week_start': 'sunday',
            'model_imagination': 'low'
        }
        res = self.client.put(PROFILE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        for key, value in payload.items():
            if key in ['day_start', 'day_end']:
                self.assertEqual(getattr(self.profile, key), datetime.strptime(value, '%H:%M:%S').time())
            else:
                self.assertEqual(getattr(self.profile, key), value)

    def test_update_invalid_morning_intention(self):
        payload = {'morning_intention_id': 999}
        res = self.client.patch(PROFILE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_invalid_evening_reflection(self):
        payload = {'evening_reflection_id': 999}
        res = self.client.patch(PROFILE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
