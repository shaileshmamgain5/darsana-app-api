"""
Database models.
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

import random


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
    expires_at = models.DateTimeField(
        default=timezone.now() + timezone.timedelta(days=1)
    )

    class Meta:
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'

    def save(self, *args, **kwargs):
        if not self.verification_pin:
            self.verification_pin = self.generate_pin()
        if not self.pk:  # Only set expires_at when creating a new object
            self.expires_at = timezone.now() + timezone.timedelta(days=1)
        super().save(*args, **kwargs)

    def generate_new_pin(self):
        self.verification_pin = self.generate_pin()
        self.expires_at = timezone.now() + timezone.timedelta(days=1)
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
    description = models.TextField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
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
    tags = models.ManyToManyField('Tag', blank=True)
    is_system_created = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # The 'related_name' allows reverse lookup from User to quotes
    favorited_by = models.ManyToManyField(
        get_user_model(),
        related_name='favorite_journals',
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
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class BasePrompt(models.Model):
    prompt_text = models.TextField()
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
    journal = models.ForeignKey(
        JournalTemplate,
        on_delete=models.CASCADE,
        related_name='base_prompts',
        null=True,
        blank=True
    )  # Belongs to a journal if it's part of a base prompt sequence
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Journal Entry by {self.user.username}"


class PromptEntry(models.Model):
    journal_entry = models.ForeignKey(
        JournalEntry, 
        on_delete=models.CASCADE, 
        related_name='prompt_entries'
    )  # Links the prompt entry to a journal entry
    
    user_prompt_text = models.TextField(blank=True, null=True)  # Optional user-generated prompt for plain entries
    user_response_text = models.TextField(blank=True, null=True)  # The user's response

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prompt Entry by {self.journal_entry.user.username}"


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


# Goals

class Goal(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    repeats = models.CharField(
        max_length=10,
        choices=RepeatType.choices,
        default=RepeatType.DAILY
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Goal'
        verbose_name_plural = 'Goals'

    def __str__(self):
        return f"{self.title} - {self.user.email}"


class GoalRepetition(models.Model):
    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        related_name='repetitions'
    )  # The goal this repetition belongs to
    repeat_type = models.CharField(
        max_length=10,
        choices=RepeatType.choices,
        default=RepeatType.DAILY
    )  # Specifies if the repetition is weekly or monthly
    days_of_week = models.ManyToManyField(
        DayOfWeek,
        blank=True
    )  # Allows selecting multiple days of the week for weekly goals
    days_of_month = models.ManyToManyField(
        DayOfMonth,
        blank=True
    )  # Allows selecting multiple days of the month for monthly goals
    last_day_of_month = models.BooleanField(default=False)  # If the goal repeats on the last day of the month

    def __str__(self):
        if self.repeat_type == RepeatType.WEEKLY:
            days = ', '.join([day.__str__() for day in self.days_of_week.all()])
            return f"{self.goal.title} repeats weekly on {days}"
        elif self.repeat_type == RepeatType.MONTHLY:
            if self.last_day_of_month:
                return f"{self.goal.title} repeats on the last day of the month"
            else:
                days = ', '.join([str(day) for day in self.days_of_month.all()])
                return f"{self.goal.title} repeats monthly on days {days}"
        return f"{self.goal.title} repeats {self.get_repeat_type_display()}"


class GoalCompletion(models.Model):
    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        related_name='completions'
    )  # The goal being tracked
    date = models.DateField()  # Date the goal was completed
    is_completed = models.BooleanField(default=False)  # Whether the goal was completed on this date

    def __str__(self):
        return f"{self.goal.title} - {self.date} - {'Completed' if self.is_completed else 'Not Completed'}"


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
    name = models.CharField(max_length=255)  # User's display name
    email = models.EmailField()  # User's email address
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
        return f"{self.user.username}'s Profile"


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
        return f"Subscription for {self.user_profile.user.username} - {self.subscription_plan.name}"

    def is_active(self):
        return self.status == 'active' and (self.end_date is None or self.end_date > timezone.now().date())
