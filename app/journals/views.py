from rest_framework import viewsets, permissions
from core.models import JournalTemplate, JournalTopic, JournalPrompt, JournalEntry, PromptEntry
from .serializers import JournalTemplateSerializer, JournalTopicSerializer, JournalPromptSerializer, JournalEntrySerializer, PromptEntrySerializer
from core.utils import IsOwnerOrReadOnly

class JournalTemplateViewSet(viewsets.ModelViewSet):
    queryset = JournalTemplate.objects.all()
    serializer_class = JournalTemplateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        return JournalTemplate.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            cover_image=self.request.FILES.get('cover_image')
        )

    def perform_update(self, serializer):
        if 'cover_image' in self.request.FILES:
            serializer.save(cover_image=self.request.FILES['cover_image'])
        else:
            serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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