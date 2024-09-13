from rest_framework import generics, permissions
from core.models import Thread, ChatSession, ChatMessage
from .serializers import ThreadSerializer, ChatSessionSerializer, ChatMessageSerializer
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

class ThreadListCreateView(generics.ListCreateAPIView):
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ThreadDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(user=self.request.user)

class ChatSessionListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        thread_id = self.kwargs['thread_id']
        return ChatSession.objects.filter(thread_id=thread_id, thread__user=self.request.user)

    def perform_create(self, serializer):
        thread_id = self.kwargs['thread_id']
        thread = Thread.objects.get(id=thread_id)
        if thread.user != self.request.user:
            raise PermissionDenied(
                "You do not have permission to create a \
                    chat session for this thread."
            )
        serializer.save(thread_id=thread_id)

class ChatSessionDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(thread__user=self.request.user)

    def perform_update(self, serializer):
        if 'ended_at' in self.request.data and not serializer.instance.ended_at:
            serializer.save(ended_at=timezone.now())
        else:
            serializer.save()

class ChatMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        session_id = self.kwargs['session_id']
        return ChatMessage.objects.filter(
            chat_session_id=session_id,
            chat_session__thread__user=self.request.user
        )

    def perform_create(self, serializer):
        session_id = self.kwargs['session_id']
        chat_session = ChatSession.objects.get(id=session_id)
        if chat_session.thread.user != self.request.user:
            raise PermissionDenied(
                "You do not have permission to create a \
                    message for this chat session."
            )
        serializer.save(chat_session_id=session_id)
