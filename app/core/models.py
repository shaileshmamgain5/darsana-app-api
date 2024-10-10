"""
Database models.
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

import random


def get_email_verification_expiration_date():
    return timezone.now() + timezone.timedelta(days=1)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """
        Create save and return a new user, in django it creates
        a new user model. manager uses the model.
        """
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # encrypt password
        user.set_password(password)
        # save to db
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # assign a user manager to this class
    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email


class EmailVerification(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='email_verification'
    )
    verification_pin = models.CharField(max_length=6, editable=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(default=get_email_verification_expiration_date)

    class Meta:
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'

    def save(self, *args, **kwargs):
        if not self.verification_pin:
            self.verification_pin = self.generate_pin()
        if not self.pk:  # Only set expires_at when creating a new object
            self.expires_at = get_email_verification_expiration_date()
        super().save(*args, **kwargs)

    def generate_new_pin(self):
        self.verification_pin = self.generate_pin()
        self.expires_at = get_email_verification_expiration_date()
        self.save()

    @staticmethod
    def generate_pin():
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def __str__(self):
        return f"Verification for {self.user.email}"


#Features
class Visibility(models.TextChoices):
    PUBLIC = 'public', 'Public'
    PRIVATE = 'private', 'Private'
    FRIENDS = 'friends', 'Friends'


class RepeatType(models.TextChoices):
    NONE = 'none', 'None'
    DAILY = 'daily', 'Daily'
    WEEKLY = 'weekly', 'Weekly'
    MONTHLY = 'monthly', 'Monthly'


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        related_name='categories',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class DayOfWeek(models.Model):
    day = models.CharField(
        max_length=2,
        choices=[
            ('M', 'Monday'),
            ('T', 'Tuesday'),
            ('W', 'Wednesday'),
            ('Th', 'Thursday'),
            ('F', 'Friday'),
            ('S', 'Saturday'),
            ('Su', 'Sunday')
        ]
    )
    def __str__(self):
        return self.get_day_display()

class DayOfMonth(models.Model):
    day = models.IntegerField()  # Day of the month (1-31)

    def __str__(self):
        return str(self.day)

    def clean(self):
        if self.day < 1 or self.day > 31:
            raise ValidationError('Day must be between 1 and 31.')

class JournalTemplate(models.Model):
    # user who created the journal, null if system created
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journal_templates'
    )
    title = models.CharField(max_length=255)
    description = models.JSONField(default=list, blank=True, null=True)
    additional_info = models.JSONField(default=list, blank=True, null=True)
    cover_image = models.ImageField(
        upload_to='journal_covers/',
        blank=True,
        null=True
    )
    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.PRIVATE
    )
    tags = models.ManyToManyField(
        'Tag',
        blank=True
    )
    is_system_created = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # The 'related_name' allows reverse lookup from User to quotes
    favorited_by = models.ManyToManyField(
        get_user_model(),
        related_name='favorite_journals',
        blank=True
    )
    category = models.ManyToManyField(
        'Category',
        blank=True
    )

    class Meta:
        verbose_name = 'Journal Template'
        verbose_name_plural = 'Journal Templates'

    def __str__(self):
        return self.title

    def mark_as_favorite(self, user):
        """Add user to the list of those \
            who favorited this journal template."""
        self.favorited_by.add(user)

    def remove_favorite(self, user):
        """Remove user from the list of those
        who favorited this journal template."""
        self.favorited_by.remove(user)

    def is_favorited_by(self, user):
        return self.favorited_by.filter(id=user.id).exists()


class JournalTopic(models.Model):
    journal = models.ForeignKey(JournalTemplate, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=255)
    description = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return self.title


class BasePrompt(models.Model):
    prompt_text = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_answer_required = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class JournalPrompt(BasePrompt):
    topic = models.ForeignKey(
        JournalTopic,
        on_delete=models.SET_NULL,
        related_name='prompts',
        null=True,
        blank=True
    )  # A prompt belongs to a topic, but it can be null if it's a base prompt
    order = models.IntegerField()  # Defines the order of the prompt in the sequence

    def __str__(self):
        return self.prompt_text[:50]

class StandalonePrompt(BasePrompt):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )  # Null if created by system
    title = models.CharField(max_length=255)  # Title for the standalone prompt
    tags = models.ManyToManyField('Tag', blank=True)  # Tags for standalone prompts
    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.PRIVATE
    )
    is_system_created = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class JournalEntry(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    journal_template = models.ForeignKey(
        'JournalTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journal_entries'
    )  # The journal template used (if any)
    standalone_prompt = models.ForeignKey(
        'StandalonePrompt',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    is_completed = models.BooleanField(default=False)
    is_started = models.BooleanField(default=False)
    for_date = models.DateField(null=True, blank=True) # The date for which the journal entry is intended
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Journal Entry by {self.user.email}"


class PromptEntry(models.Model):
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='prompt_entries'
    )  # Links the prompt entry to a journal entry

    user_prompt_text = models.JSONField(default=list, blank=True, null=True)  # Optional user-generated prompt for plain entries
    user_response_text = models.JSONField(default=list, blank=True, null=True)  # The user's response

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prompt Entry by {self.journal_entry.user.email}"


class Quote(models.Model):
    text = models.TextField()
    author = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag, blank=True)  # Quote has multiple tags

    # The 'related_name' allows reverse lookup from User to quotes
    favorited_by = models.ManyToManyField(User, related_name='favorite_quotes', blank=True)

    def __str__(self):
        return f'"{self.text}" - {self.author}'

    def mark_as_favorite(self, user):
        """Add user to the list of those who favorited this quote."""
        self.favorited_by.add(user)

    def remove_favorite(self, user):
        """Remove user from the list of those who favorited this quote."""
        self.favorited_by.remove(user)

    def is_favorited_by(self, user):
        """Check if the quote is favorited by a specific user."""
        return self.favorited_by.filter(id=user.id).exists()

    class Meta:
        verbose_name = 'Quote'
        verbose_name_plural = 'Quotes'

# ... existing code ...


class JournalSummary(models.Model):
    RATING_CHOICES = [
        (1, 'Not Helpful'),
        (2, 'Somewhat Helpful'),
        (3, 'Very Helpful'),
    ]

    journal_entry = models.OneToOneField(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='summary'
    )
    title = models.CharField(max_length=255)
    summary_text = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    mood = models.CharField(max_length=50, blank=True, null=True)
    key_points = models.JSONField(default=list, blank=True, null=True)
    user_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"Summary for {self.journal_entry}"

    class Meta:
        verbose_name = 'Journal Summary'
        verbose_name_plural = 'Journal Summaries'


# Goals

class Goal(models.Model):
    REPEAT_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    repeat_type = models.CharField(max_length=10, choices=REPEAT_CHOICES, default='daily')
    is_active = models.BooleanField(default=True)
    progress = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return f"{self.title} - {self.user.email}"

    def is_due_today(self):
        today = timezone.now().date()
        if not self.is_active or (self.end_date and self.end_date < today):
            return False

        if self.repeat_type == 'daily':
            return True
        elif self.repeat_type == 'weekly':
            return today.weekday() in self.repetition.repeat_on.get('days_of_week', [])
        elif self.repeat_type == 'monthly':
            return today.day in self.repetition.repeat_on.get('days_of_month', [])
        elif self.repeat_type == 'custom':
            # Implement custom logic based on frequency and repeat_on data
            pass

        return False

class GoalRepetition(models.Model):
    goal = models.OneToOneField(Goal, on_delete=models.CASCADE, related_name='repetition')
    repeat_on = models.JSONField(default=dict)  # Store repetition data for all types
    frequency = models.PositiveIntegerField(default=1)  # e.g., every 1 week, every 2 months

    def __str__(self):
        return f"Repetition for {self.goal.title}"

class GoalCompletion(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='completions')
    date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completion_value = models.FloatField(null=True, blank=True)  # For quantitative tracking
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['goal', 'date']

    def __str__(self):
        return f"{self.goal.title} - {self.date} - {'Completed' if self.is_completed else 'Not Completed'}"

# Chat

class Thread(models.Model):
    """ A Thread represents an ongoing conversation topic\
          and can contain multiple ChatSessions.
    """
    title = models.CharField(max_length=200)
    cover_message = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} (User: {self.user.email})"

class ChatSession(models.Model):
    """ A ChatSession represents a single chat session\
          within a thread.
    """
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    # Maintaining the context ChatSessions
    session_summary = models.TextField(blank=True, null=True)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session for {self.thread.title}"

class ChatMessage(models.Model):
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(
        max_length=20,
        choices=[('user', 'User'), ('assistant', 'Assistant'), ('system', 'System')]
    )
    text = models.JSONField(default=list)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Message from {self.sender} in {self.chat_session}"


class ModelConfiguration(models.Model):
    name = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=50)
    temperature = models.FloatField()
    question_prompt = models.TextField()
    response_prompt = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class PerformanceMetric(models.Model):
    configuration = models.ForeignKey(ModelConfiguration, on_delete=models.CASCADE)
    average_response_time = models.FloatField(default=0)
    average_session_length = models.FloatField(default=0)
    like_count = models.IntegerField(default=0)
    dislike_count = models.IntegerField(default=0)
    total_messages = models.IntegerField(default=0)

    def __str__(self):
        return f"Metrics for {self.configuration.name}"


# Moods


class MoodEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user who submitted the mood
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the mood was recorded
    mood_value = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )  # Value from the slider, now locked between 1 and 5
    mood_description = models.TextField(blank=True, null=True)  # Optional description or note about the mood

    def __str__(self):
        return f"Mood Entry for {self.user.email} at {self.created_at}"


class MoodTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    for_value = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return f"{self.name} (for mood value: {self.for_value})"


class MoodResponse(models.Model):
    mood_entry = models.ForeignKey(MoodEntry, on_delete=models.CASCADE, related_name='responses')  # Link to the mood entry
    mood_tags = models.ManyToManyField(MoodTag, blank=True)  # Tags describing the mood

    def __str__(self):
        tags = ', '.join([tag.name for tag in self.mood_tags.all()])
        return f"Mood Response: {self.mood_entry.user.email} | Tags: {tags}"


# Profile


class Profile(models.Model):
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]

    WEEK_START_CHOICES = [
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
    ]

    MODEL_IMAGINATION_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE
    )  # Links to the User model
    name = models.CharField(max_length=255, blank=True)  # User's display name
    email = models.EmailField(blank=True)  # User's email address
    subscription_details = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )  # Subscription plan details
    morning_intention = models.OneToOneField(
        'JournalTemplate',
        related_name='morning_intention',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )  # Morning reflection journal
    evening_reflection = models.OneToOneField(
        'JournalTemplate',
        related_name='evening_reflection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )  # Evening reflection journal
    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default='light'
    )
    day_start = models.TimeField(default='08:00:00')
    day_end = models.TimeField(default='20:00:00')
    week_start = models.CharField(
        max_length=10,
        choices=WEEK_START_CHOICES,
        default='sunday'
    )
    model_imagination = models.CharField(
        max_length=10,
        choices=MODEL_IMAGINATION_CHOICES,
        default='moderate'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"


class SubscriptionPlan(models.Model):
    PLATFORM_CHOICES = [
        ('google', 'Google Play'),
        ('apple', 'Apple App Store'),
    ]

    name = models.CharField(max_length=50)  # Name of the subscription plan (e.g., Monthly, Yearly)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)  # Platform: Google or Apple
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the subscription plan
    duration_days = models.IntegerField()  # Duration of the subscription in days
    description = models.TextField(blank=True, null=True)  # Description of the plan, if needed

    def __str__(self):
        return f"{self.name} ({self.platform}) - {self.price} USD"


class UserSubscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('expired', 'Expired'),
        ('trial', 'Trial'),
    ]

    user_profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='user_subscription'
    )
    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True
    )
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='trial'
    )
    receipt_token = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )  # Google/Apple receipt token
    transaction_id = models.CharField(
        max_length=255,
        unique=True
    )  # Google/Apple transaction ID

    def __str__(self):
        return f"Subscription for {self.user_profile.user.email} - {self.subscription_plan.name}"

    def is_active(self):
        return self.status == 'active' and (self.end_date is None or self.end_date > timezone.now().date())

class AppConfiguration(models.Model):
    version = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=False)
    configurations = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"App Configuration v{self.version}"

    def save(self, *args, **kwargs):
        if self.is_active:
            # Set all other configurations to inactive
            AppConfiguration.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
