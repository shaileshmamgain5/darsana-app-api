from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError

from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


def send_verification_email(user, verification_pin):
    subject = 'Verify your email with Darsana'
    message = f'Your verification pin is: {verification_pin}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    try:
        if settings.DEBUG:
            print(
                f"DEBUG: Email not sent. Verification pin for {user.email}: {verification_pin}" # noqa
                )
        else:
            print(
                f"Sending email to {user.email} with subject: {subject} from {from_email}" # noqa
                )
            send_mail(
                subject,
                message,
                from_email,
                recipient_list
            )
    except Exception as e:
        raise ValidationError(f"Failed to send verification email: {str(e)}")
