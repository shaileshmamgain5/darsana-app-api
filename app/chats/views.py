from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from core.models import (
    Thread,
    ChatSession,
    ChatMessage,
    ModelConfiguration,
    PerformanceMetric
)
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
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

import requests
import time
from services.chat_service import ChatService


class GetResponseView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=OpenApiTypes.OBJECT,
        responses={200: OpenApiTypes.OBJECT},
        description='Get an AI response for a given message',
        examples=[
            OpenApiExample(
                'Example request',
                value={
                    'message': 'Hello, how are you?',
                    'session_id': 1,
                    'thread_id': None
                },
                request_only=True,
            ),
            OpenApiExample(
                'Example response',
                value={
                    'session_id': 1,
                    'thread_id': 1,
                    'ai_response': {
                        'id': 1,
                        'sender': 'assistant',
                        'text': "Hello! I'm doing well, thank you for asking. How can I assist you today?",
                        'timestamp': '2023-05-17T10:30:00Z',
                        'action': None,
                        'metadata': {}
                    }
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        """
        Get an AI response for a given message.

        This endpoint accepts a user message and optional session_id or thread_id.
        It returns an AI-generated response along with session and thread information.

        If neither session_id nor thread_id is provided, a new thread and session are created.
        """
        message = request.data.get('message')
        session_id = request.data.get('session_id')
        thread_id = request.data.get('thread_id')
        print(f"Received message: {request.data}")

        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            chat_service = ChatService(request.user)
            response_data = chat_service.process_message(message, session_id, thread_id)
            if response_data:
                return Response(response_data)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, exception):
        if isinstance(exception, (ChatSession.DoesNotExist, Thread.DoesNotExist)):
            return Response({'error': 'Invalid session_id or thread_id'}, status=status.HTTP_404_NOT_FOUND)
        elif isinstance(exception, requests.ConnectionError):
            return Response({'error': 'Unable to connect to assistant service'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        elif isinstance(exception, requests.Timeout):
            return Response({'error': 'Assistant service request timed out'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        elif isinstance(exception, requests.HTTPError):
            return Response({'error': f'Assistant service error: {exception.response.status_code}'}, status=status.HTTP_502_BAD_GATEWAY)
        elif isinstance(exception, requests.RequestException):
            return Response({'error': 'Error processing assistant response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': str(exception)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, thread_id):
        try:
            thread = Thread.objects.get(id=thread_id, user=request.user)
            latest_user_message = ChatMessage.objects.filter(
                chat_session__thread=thread,
                sender='user'
            ).order_by('-timestamp').first()

            if not latest_user_message:
                return Response({'error': 'No user message found in this thread'}, status=status.HTTP_404_NOT_FOUND)

            ChatService.cancel_request(request.user.id, latest_user_message.text)

            system_message = ChatMessage.objects.create(
                chat_session=latest_user_message.chat_session,
                sender='system',
                text='Response cancelled'
            )

            return Response(ChatMessageSerializer(system_message).data)
        except Thread.DoesNotExist:
            return Response({'error': 'Thread not found'}, status=status.HTTP_404_NOT_FOUND)


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


class FeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        message = ChatMessage.objects.get(id=message_id)
        feedback = request.data.get('feedback')

        configuration = ModelConfiguration.objects.filter(is_active=True).first()
        metric = PerformanceMetric.objects.get(configuration=configuration)

        if feedback == 'like':
            metric.like_count += 1
        elif feedback == 'dislike':
            metric.dislike_count += 1

        metric.save()

        return Response({'status': 'Feedback recorded'})
