from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError

from rest_framework import permissions
from core.models import JournalTemplate, JournalPrompt
from django.db import transaction

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

def create_journal_deep_copy(original_journal, user):
    new_journal = JournalTemplate.objects.create(
        user=user,
        title=original_journal.title,
        description=original_journal.description,
        additional_info=original_journal.additional_info,
        visibility='private'
    )

    # Copy associated prompts
    for prompt in original_journal.journal_prompts.all():
        new_prompt = JournalPrompt.objects.create(
            topic=new_journal.topics.first(),  # Assuming the first topic
            prompt_text=prompt.prompt_text,
            description=prompt.description,
            is_answer_required=prompt.is_answer_required,
            order=prompt.order
        )
        new_prompt.tags.set(prompt.tags.all())

    return new_journal

def copy_default_daily_journals(user):
    default_journal_ids = [1, 2]
    for journal_id in default_journal_ids:
        try:
            original_journal = JournalTemplate.objects.get(id=journal_id)
            new_journal = create_journal_deep_copy(original_journal, user)

            # Set morning and evening journals
            if journal_id == 1:
                user.profile.morning_intention = new_journal
            elif journal_id == 2:
                user.profile.evening_reflection = new_journal
            user.profile.save()
        except JournalTemplate.DoesNotExist:
            pass
