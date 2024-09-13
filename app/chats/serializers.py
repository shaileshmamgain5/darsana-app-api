from rest_framework import serializers
from core.models import Thread, ChatSession, ChatMessage

class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['id', 'thread', 'started_at', 'ended_at', 'context']
        read_only_fields = ['id', 'thread', 'started_at', 'ended_at']

class ThreadSerializer(serializers.ModelSerializer):
    sessions = ChatSessionSerializer(many=True, read_only=True)

    class Meta:
        model = Thread
        fields = ['id', 'title', 'user', 'created_at', 'updated_at', 'is_archived', 'sessions']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'chat_session', 'sender', 'text', 'timestamp', 'action', 'metadata']
        read_only_fields = ['id', 'chat_session', 'timestamp']
