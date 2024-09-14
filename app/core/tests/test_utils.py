from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import JournalTemplate, Profile
from core.utils import copy_default_daily_journals
from core.constants import DEFAULT_MORNING_JOURNAL_ID, DEFAULT_EVENING_JOURNAL_ID
from django.db import transaction
from unittest.mock import patch

class UtilsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.create(user=self.user)

    def test_copy_default_daily_journals(self):
        morning_journal = JournalTemplate.objects.create(title="Morning Journal")
        evening_journal = JournalTemplate.objects.create(title="Evening Journal")

        with patch('core.utils.DEFAULT_MORNING_JOURNAL_ID', morning_journal.id):
            with patch('core.utils.DEFAULT_EVENING_JOURNAL_ID', evening_journal.id):
                with patch('core.utils.DEFAULT_JOURNAL_IDS', [morning_journal.id, evening_journal.id]):
                    with transaction.atomic():
                        copy_default_daily_journals(self.user)

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.profile.morning_intention)
        self.assertIsNotNone(self.user.profile.evening_reflection)
        self.assertEqual(self.user.profile.morning_intention.title, "Morning Journal")
        self.assertEqual(self.user.profile.evening_reflection.title, "Evening Journal")

    def test_copy_default_daily_journals_missing_template(self):
        # Create a journal without specifying an ID
        morning_journal = JournalTemplate.objects.create(title="Morning Journal")
        # Set the constant to use the created journal's ID
        with patch('core.utils.DEFAULT_MORNING_JOURNAL_ID', morning_journal.id):
            with patch('core.utils.DEFAULT_EVENING_JOURNAL_ID', 55):
                with patch('core.utils.DEFAULT_JOURNAL_IDS', [morning_journal.id, 55]):
                    with transaction.atomic():
                        copy_default_daily_journals(self.user)

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.profile.morning_intention)
        self.assertIsNone(self.user.profile.evening_reflection)
        self.assertEqual(self.user.profile.morning_intention.title, "Morning Journal")

    def test_copy_default_daily_journals_no_templates(self):
        with transaction.atomic():
            copy_default_daily_journals(self.user)

        self.user.refresh_from_db()
        self.assertIsNone(self.user.profile.morning_intention)
        self.assertIsNone(self.user.profile.evening_reflection)
