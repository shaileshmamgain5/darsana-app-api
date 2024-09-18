from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from core.models import ChatSession

@shared_task
def close_inactive_sessions():
    timeout_duration = timedelta(hours=4)  # Adjust as needed
    inactive_time = timezone.now() - timeout_duration
    
    inactive_sessions = ChatSession.objects.filter(
        ended_at__isnull=True,
        last_activity__lt=inactive_time
    )
    
    for session in inactive_sessions:
        session.ended_at = timezone.now()
        session.save()

    return f"Closed {inactive_sessions.count()} inactive sessions."
