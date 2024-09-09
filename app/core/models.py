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
