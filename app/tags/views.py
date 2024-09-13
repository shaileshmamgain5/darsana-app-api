from django.shortcuts import render
from rest_framework import viewsets
from core.models import Tag
from .serializers import TagSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from core.utils import IsOwnerOrReadOnly

# Create your views here.

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()
