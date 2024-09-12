from rest_framework import viewsets, permissions
from core.models import JournalTemplate, JournalTopic, JournalPrompt, JournalEntry, PromptEntry
from .serializers import JournalTemplateSerializer, JournalTopicSerializer, JournalPromptSerializer, JournalEntrySerializer, PromptEntrySerializer
from core.utils import IsOwnerOrReadOnly

class JournalTemplateViewSet(viewsets.ModelViewSet):
    queryset = JournalTemplate.objects.all()
    serializer_class = JournalTemplateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class JournalTopicViewSet(viewsets.ModelViewSet):
    queryset = JournalTopic.objects.all()
    serializer_class = JournalTopicSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

class JournalPromptViewSet(viewsets.ModelViewSet):
    queryset = JournalPrompt.objects.all()
    serializer_class = JournalPromptSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

class JournalEntryViewSet(viewsets.ModelViewSet):
    serializer_class = JournalEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PromptEntryViewSet(viewsets.ModelViewSet):
    serializer_class = PromptEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return PromptEntry.objects.filter(journal_entry__user=self.request.user)