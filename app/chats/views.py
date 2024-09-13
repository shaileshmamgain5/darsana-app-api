from rest_framework import generics, permissions
from core.models import Thread, ChatSession, ChatMessage
from .serializers import ThreadSerializer, ChatSessionSerializer, ChatMessageSerializer
from django.utils import timezone

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
        return ChatSession.objects.filter(thread_id=thread_id, user=self.request.user)

    def perform_create(self, serializer):
        thread_id = self.kwargs['thread_id']
        serializer.save(user=self.request.user, thread_id=thread_id)

class ChatSessionDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

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
        return ChatMessage.objects.filter(chat_session_id=session_id)

    def perform_create(self, serializer):
        session_id = self.kwargs['session_id']
        serializer.save(chat_session_id=session_id)
