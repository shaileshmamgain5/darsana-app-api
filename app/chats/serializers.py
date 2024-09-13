from rest_framework import serializers
from core.models import Thread, ChatSession, ChatMessage

class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ['id', 'title', 'created_at', 'updated_at', 'is_archived']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['id', 'thread', 'started_at', 'ended_at', 'context']
        read_only_fields = ['id', 'thread', 'started_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'chat_session', 'sender', 'text', 'timestamp', 'action', 'metadata']
        read_only_fields = ['id', 'chat_session', 'timestamp']
