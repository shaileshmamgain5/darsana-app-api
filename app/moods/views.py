from rest_framework import viewsets, permissions
from core.models import MoodEntry, MoodTag
from .serializers import MoodEntrySerializer, MoodTagSerializer

# Create your views here.

class MoodEntryViewSet(viewsets.ModelViewSet):
    serializer_class = MoodEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MoodEntry.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MoodTagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MoodTag.objects.all()
    serializer_class = MoodTagSerializer
    permission_classes = [permissions.IsAuthenticated]
