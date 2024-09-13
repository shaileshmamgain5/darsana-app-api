from django.shortcuts import render
from rest_framework import viewsets
from core.models import StandalonePrompt
from .serializers import StandalonePromptSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class StandalonePromptViewSet(viewsets.ModelViewSet):
    queryset = StandalonePrompt.objects.all()
    serializer_class = StandalonePromptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return StandalonePrompt.objects.filter(user=user) | StandalonePrompt.objects.filter(visibility='public')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
