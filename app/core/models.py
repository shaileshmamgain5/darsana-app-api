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
import random
from django.utils import timezone
from datetime import timedelta


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

    # assign a user manager to this class
    objects = UserManager()

    USERNAME_FIELD = 'email'


class EmailVerification(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    verification_pin = models.CharField(max_length=6, editable=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        default=timezone.now() + timedelta(days=1)
    )

    def save(self, *args, **kwargs):
        if not self.verification_pin:
            self.verification_pin = ''.join(
                [str(random.randint(0, 9)) for _ in range(6)]
            )
        if not self.pk:  # Only set expires_at when creating a new object
            self.expires_at = timezone.now() + timedelta(days=1)
        super().save(*args, **kwargs)

    def generate_new_pin(self):
        self.verification_pin = ''.join(
            [str(random.randint(0, 9)) for _ in range(6)]
            )
        self.expires_at = timezone.now() + timezone.timedelta(days=1)
        self.save()


#Features


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


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


class Journal(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    # user who created the journal, null if system created
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)  # Any additional information
    cover_image = models.ImageField(
        upload_to='journal_covers/',
        blank=True,
        null=True
    )
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='private'
    )
    tags = models.ManyToManyField(Tag, blank=True)  # Journal has multiple tags
    is_system_created = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Topic(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='topics')  # Journal to which this topic belongs
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class BasePrompt(models.Model):
    prompt_text = models.TextField()  # The text of the prompt
    description = models.TextField(blank=True, null=True) # about the prompt
    is_answer_required = models.BooleanField(default=True)  # Whether the prompt requires an answer
    tags = models.ManyToManyField(Tag, blank=True)  # Tags for categorization
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True  # This makes it an abstract base class


class JournalPrompt(BasePrompt):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='prompts',
        null=True,
        blank=True
    )  # A prompt belongs to a topic, but it can be null if it's a base prompt
    journal = models.ForeignKey(
        Journal,
        on_delete=models.CASCADE,
        related_name='base_prompts',
        null=True,
        blank=True
    )  # Belongs to a journal if it's part of a base prompt sequence
    order = models.IntegerField()  # Defines the order of the prompt in the sequence

    def __str__(self):
        return self.prompt_text[:50]  # Show the first 50 characters of the prompt


class StandalonePrompt(BasePrompt):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )  # Null if created by system
    title = models.CharField(max_length=255)  # Title for the standalone prompt
    tags = models.ManyToManyField('Tag', blank=True)  # Tags for standalone prompts
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='private'
    )
    is_system_created = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class PromptResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user responding to the prompt
    prompt_text = models.ForeignKey(
        JournalPrompt,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )  # Response to a journal prompt
    standalone_prompt = models.ForeignKey(
        StandalonePrompt,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )  # Response to a standalone prompt
    # response prompt can be different from the prompt text
    response_prompt_text = models.TextField(blank=True, null=True)
    response_text = models.TextField(
        blank=True,
        null=True
    )  # The response text

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Response by {self.user.username}"


class PromptResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    journal_prompt = models.ForeignKey(
        JournalPrompt,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    standalone_prompt = models.ForeignKey(
        StandalonePrompt,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.journal_prompt:
            return f"Response by {self.user.username} to Journal Prompt: {self.journal_prompt.prompt_text[:50]}"
        return f"Response by {self.user.username} to Standalone Prompt: {self.standalone_prompt.prompt_text[:50]}"


# Goals

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user who created the goal
    title = models.CharField(max_length=255)  # Goal title (e.g., "Take a 30 min walk")
    description = models.TextField(blank=True, null=True)  # Optional description (e.g., why it's important)
    created_at = models.DateTimeField(auto_now_add=True)  # Goal creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last updated timestamp
    repeats = models.CharField(
        max_length=10,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly')
        ],
        default='daily'
    )
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


class GoalRepetition(models.Model):
    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        related_name='repetitions'
    )  # The goal this repetition belongs to
    repeat_type = models.CharField(
        max_length=10,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly')
        ]
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
        if self.repeat_type == 'weekly':
            days = ', '.join([day.__str__() for day in self.days_of_week.all()])
            return f"{self.goal.title} repeats weekly on {days}"
        elif self.repeat_type == 'monthly':
            if self.last_day_of_month:
                return f"{self.goal.title} repeats on the last day of the month"
            else:
                days = ', '.join([str(day) for day in self.days_of_month.all()])
                return f"{self.goal.title} repeats monthly on days {days}"


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
        User,
        on_delete=models.CASCADE
    )  # Links to the User model
    name = models.CharField(max_length=255)  # User's display name
    email = models.EmailField()  # User's email address
    subscription = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )  # Subscription plan details
    morning_intention = models.OneToOneField(
        'Journal',
        related_name='morning_intention',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )  # Morning reflection journal
    evening_reflection = models.OneToOneField(
        'Journal',
        related_name='evening_reflection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )  # Evening reflection journal
    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default='light'
    )  # Theme preference
    day_start = models.TimeField(default='08:00:00')  # The time when the user’s day starts
    day_end = models.TimeField(default='20:00:00')  # The time when the user’s day ends
    week_start = models.CharField(
        max_length=10,
        choices=WEEK_START_CHOICES,
        default='sunday'
    )  # Week starting day
    model_imagination = models.CharField(
        max_length=10,
        choices=MODEL_IMAGINATION_CHOICES,
        default='moderate'
    )  # Imagination level of the AI model
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
        'UserProfile',
        on_delete=models.CASCADE,
        related_name='subscription'
    )  # Link to UserProfile
    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True
    )  # The selected subscription plan
    start_date = models.DateField(default=timezone.now)  # When the subscription started
    end_date = models.DateField(blank=True, null=True)  # When the subscription will end
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='trial'
    )  # The status of the subscription
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
        """
        Returns whether the subscription is currently active.
        """
        return self.status == 'active' and (self.end_date is None or self.end_date > timezone.now)
