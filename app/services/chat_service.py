from core.models import Thread, ChatSession, ChatMessage, ModelConfiguration, PerformanceMetric
from chats.serializers import ChatMessageSerializer
from services.langserve_client import LangServeClient
import time

class ChatService:
    def __init__(self, user):
        self.user = user
        self.langserve_client = LangServeClient()

    def process_message(self, message, session_id, thread_id):
        session, thread = self._get_or_create_session(session_id, thread_id)
        user_message = self._save_user_message(session, message)
        self._update_thread_cover_message(thread, message)
        thread_messages = self._get_thread_messages(thread)
        ai_response = self._get_ai_response(message, thread_messages)
        ai_message = self._save_ai_message(session, ai_response)
        self._update_performance_metrics(ai_response)
        
        return {
            'session_id': session.id,
            'thread_id': thread.id,
            'ai_response': ChatMessageSerializer(ai_message).data
        }

    def _get_or_create_session(self, session_id, thread_id):
        if session_id:
            session = ChatSession.objects.get(id=session_id)
            thread = session.thread
        elif thread_id:
            thread = Thread.objects.get(id=thread_id)
            session = ChatSession.objects.create(thread=thread)
        else:
            thread = Thread.objects.create(user=self.user, title="New Conversation")
            session = ChatSession.objects.create(thread=thread)
        return session, thread

    def _save_user_message(self, session, message):
        return ChatMessage.objects.create(
            chat_session=session,
            sender='user',
            text=message
        )

    def _update_thread_cover_message(self, thread, message):
        if not thread.cover_message:
            thread.cover_message = message
            thread.save()

    def _get_thread_messages(self, thread):
        return list(ChatMessage.objects.filter(chat_session__thread=thread)
                    .order_by('timestamp')
                    .values_list('sender', 'text'))

    def _get_ai_response(self, message, thread_messages):
        configuration = ModelConfiguration.objects.filter(is_active=True).first()
        return self.langserve_client.get_response(message, thread_messages, configuration.name)

    def _save_ai_message(self, session, ai_response):
        return ChatMessage.objects.create(
            chat_session=session,
            sender='assistant',
            text=ai_response
        )

    def _update_performance_metrics(self, ai_response):
        configuration = ModelConfiguration.objects.filter(is_active=True).first()
        metric, _ = PerformanceMetric.objects.get_or_create(configuration=configuration)
        metric.total_messages += 1
        metric.save()
