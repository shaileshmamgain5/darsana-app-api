from rest_framework import serializers
from core.models import Thread, ChatSession, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'text', 'timestamp', 'action', 'metadata']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'started_at', 'ended_at', 'session_summary', 'messages']

class ThreadSerializer(serializers.ModelSerializer):
    sessions = ChatSessionSerializer(many=True, read_only=True)

    class Meta:
        model = Thread
        fields = ['id', 'title', 'user', 'created_at', 'updated_at', 'is_archived', 'cover_message', 'sessions']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['sessions'] = ChatSessionSerializer(
            instance.sessions.order_by('started_at'),
            many=True
        ).data
        for session in representation['sessions']:
            session['messages'] = ChatMessageSerializer(
                ChatMessage.objects.filter(chat_session_id=session['id']).order_by('timestamp'),
                many=True
            ).data
        return representation

class ThreadListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ['id', 'title', 'cover_message', 'updated_at']
