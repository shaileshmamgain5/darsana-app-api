from rest_framework import serializers
from core.models import StandalonePrompt

class StandalonePromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = StandalonePrompt
        fields = ['id', 'user', 'title', 'prompt_text', 'description', 'is_answer_required', 'tags', 'visibility', 'is_system_created', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
