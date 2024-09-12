from rest_framework import serializers
from core.models import JournalTemplate, JournalTopic, JournalPrompt, JournalEntry, PromptEntry

class JournalTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalTopic
        fields = [
            'id',
            'title',
            'description'
        ]

class JournalPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalPrompt
        fields = [
            'id',
            'prompt_text',
            'description',
            'is_answer_required',
            'tags',
            'order'
        ]

class JournalTemplateSerializer(serializers.ModelSerializer):
    topics = JournalTopicSerializer(many=True, read_only=True)
    base_prompts = JournalPromptSerializer(many=True, read_only=True)

    class Meta:
        model = JournalTemplate
        fields = [
            'id',
            'user',
            'title',
            'description',
            'additional_info',
            'cover_image',
            'visibility',
            'tags',
            'is_system_created',
            'topics',
            'base_prompts'
        ]

class PromptEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptEntry
        fields = [
            'id',
            'journal_entry',
            'user_prompt_text',
            'user_response_text',
            'created_at'
        ]

class JournalEntrySerializer(serializers.ModelSerializer):
    prompt_entries = PromptEntrySerializer(many=True, read_only=True)

    class Meta:
        model = JournalEntry
        fields = [
            'id',
            'user',
            'journal_template',
            'standalone_prompt',
            'is_completed',
            'created_at',
            'updated_at',
            'prompt_entries'
        ]