from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import JournalTemplate, JournalTopic, JournalPrompt, Profile
from core.utils import create_journal_deep_copy, copy_default_daily_journals
from django.db import transaction

class UtilsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.create(user=self.user)

    def create_journal_template(self):
        journal = JournalTemplate.objects.create(
            title="Test Journal",
            description=["Test description"],
            additional_info=["Additional info"],
            visibility='public'
        )
        topic = JournalTopic.objects.create(
            journal=journal,
            title="Test Topic",
            description=["Topic description"]
        )
        JournalPrompt.objects.create(
            topic=topic,
            prompt_text="Test prompt",
            description="Prompt description",
            order=1
        )
        return journal

    def test_create_journal_deep_copy(self):
        original_journal = self.create_journal_template()
        copied_journal = create_journal_deep_copy(original_journal, self.user)

        self.assertNotEqual(original_journal.id, copied_journal.id)
        self.assertEqual(copied_journal.title, original_journal.title)
        self.assertEqual(copied_journal.description, original_journal.description)
        self.assertEqual(copied_journal.additional_info, original_journal.additional_info)
        self.assertEqual(copied_journal.visibility, 'private')
        self.assertEqual(copied_journal.user, self.user)

        self.assertEqual(copied_journal.topics.count(), 1)
        copied_topic = copied_journal.topics.first()
        self.assertEqual(copied_topic.title, "Test Topic")
        self.assertEqual(copied_topic.description, ["Topic description"])

        self.assertEqual(copied_topic.prompts.count(), 1)
        copied_prompt = copied_topic.prompts.first()
        self.assertEqual(copied_prompt.prompt_text, "Test prompt")
        self.assertEqual(copied_prompt.description, "Prompt description")
        self.assertEqual(copied_prompt.order, 1)

    def test_copy_default_daily_journals(self):
        JournalTemplate.objects.create(id=1, title="Morning Journal")
        JournalTemplate.objects.create(id=2, title="Evening Journal")

        with transaction.atomic():
            copy_default_daily_journals(self.user)

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.profile.morning_intention)
        self.assertIsNotNone(self.user.profile.evening_reflection)
        self.assertEqual(self.user.profile.morning_intention.title, "Morning Journal")
        self.assertEqual(self.user.profile.evening_reflection.title, "Evening Journal")

    def test_copy_default_daily_journals_missing_template(self):
        JournalTemplate.objects.create(id=1, title="Morning Journal")
        # Evening Journal (id=2) is not created

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
