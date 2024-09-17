from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from core.models import Thread, ChatSession, ChatMessage
from .serializers import (
    ChatMessageSerializer,
    ChatSessionSerializer,
    ThreadSerializer,
    ThreadListSerializer
)
from services.langserve_client import LangServeClient  # You'll need to implement this
from django.utils import timezone
from django.db.models import Prefetch
from rest_framework.permissions import IsAuthenticated


class GetResponseView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        message = request.data.get('message')
        session_id = request.data.get('session_id')
        thread_id = request.data.get('thread_id')
        thread_messages = request.data.get('thread_messages', [])

        if session_id:
            session = ChatSession.objects.get(id=session_id)
            thread = session.thread
        elif thread_id:
            thread = Thread.objects.get(id=thread_id)
            session = ChatSession.objects.create(thread=thread)
        else:
            thread = Thread.objects.create(user=request.user, title="New Conversation")
            session = ChatSession.objects.create(thread=thread)

        # Save user message
        user_message = ChatMessage.objects.create(
            chat_session=session,
            sender='user',
            text=message
        )

        # Set cover_message if it's the first message in the thread
        if not thread.cover_message:
            thread.cover_message = message
            thread.save()

        # Get AI response
        langserve_client = LangServeClient()
        ai_response = langserve_client.get_response(message, thread_messages)

        # Save AI response
        ai_message = ChatMessage.objects.create(
            chat_session=session,
            sender='ai',
            text=ai_response
        )

        return Response({
            'session_id': session.id,
            'thread_id': session.thread.id,
            'ai_response': ChatMessageSerializer(ai_message).data
        })


class CancelResponseView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, message_id):
        message = ChatMessage.objects.get(id=message_id)
        langserve_client = LangServeClient()
        langserve_client.cancel_response(message_id)

        system_message = ChatMessage.objects.create(
            chat_session=message.chat_session,
            sender='system',
            text='Response cancelled'
        )

        return Response(ChatMessageSerializer(system_message).data)


class EndSessionView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, session_id):
        session = ChatSession.objects.get(id=session_id)
        session.ended_at = timezone.now()

        # Get all messages for the session
        messages = list(session.messages.all().values('sender', 'text'))

        # Create summary using LangServe API
        langserve_client = LangServeClient()
        summary_response = langserve_client.create_summary(messages)

        summary = summary_response.get('summary', "Summary generation failed.")
        thread_title = summary_response.get('thread_title', "New Conversation")

        # Update session summary
        session.session_summary = summary
        session.save()

        # Update thread title if this is the only session
        thread = session.thread
        if thread.sessions.count() == 1:
            thread.title = thread_title
            thread.save()

        return Response({
            'message': 'Session ended',
            'summary': summary,
            'thread_title': thread_title
        })


class ThreadListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ThreadListSerializer

    def get_queryset(self):
        return Thread.objects.filter(user=self.request.user).order_by('-updated_at')


class ThreadDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ThreadSerializer

    def get_queryset(self):
        return Thread.objects.filter(user=self.request.user).prefetch_related(
            Prefetch('sessions', queryset=ChatSession.objects.order_by('started_at').prefetch_related(
                Prefetch('messages', queryset=ChatMessage.objects.order_by('timestamp'))
            ))
        )


class DeleteThreadView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Thread.objects.all()

    def perform_destroy(self, instance):
        # This will cascade delete all associated sessions and messages
        instance.delete()
