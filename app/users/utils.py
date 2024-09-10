"""
This module contains utility functions for sending verification emails.
"""
from django.core.mail import send_mail


def send_verification_email(user, verification_pin):
    send_mail(
        'Verify your email',
        f'Your verification pin is {verification_pin}',
        'from@example.com',
        [user.email],
        fail_silently=False,
    )
