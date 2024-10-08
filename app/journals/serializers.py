from rest_framework import serializers
from core.models import (
    JournalTemplate,
    JournalTopic,
    JournalPrompt,
    JournalEntry,
    PromptEntry,
    Category
)

from categories.serializers import CategorySerializer

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

class JournalTopicSerializer(serializers.ModelSerializer):
    prompts = JournalPromptSerializer(many=True)

    class Meta:
        model = JournalTopic
        fields = [
            'id',
            'title',
            'description',
            'prompts'
        ]

    def create(self, validated_data):
        prompts_data = validated_data.pop('prompts', [])
        topic = JournalTopic.objects.create(**validated_data)
        for prompt_data in prompts_data:
            tags = prompt_data.pop('tags', [])
            prompt = JournalPrompt.objects.create(topic=topic, **prompt_data)
            prompt.tags.set(tags)
        return topic

    def update(self, instance, validated_data):
        prompts_data = validated_data.pop('prompts', [])
        instance.prompts.all().delete()
        for prompt_data in prompts_data:
            tags = prompt_data.pop('tags', [])
            prompt = JournalPrompt.objects.create(topic=instance, **prompt_data)
            prompt.tags.set(tags)
        return super().update(instance, validated_data)

class JournalTemplateSerializer(serializers.ModelSerializer):
    topics = JournalTopicSerializer(many=True)
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False
    )

    class Meta:
        model = JournalTemplate
        fields = [
            'id', 'user', 'title', 'description', 'additional_info',
            'cover_image', 'visibility', 'tags', 'is_system_created',
            'topics', 'categories', 'category_ids'
        ]
        read_only_fields = ['id', 'user', 'is_system_created']

    def create(self, validated_data):
        categories = validated_data.pop('category', [])
        topics_data = validated_data.pop('topics', [])
        journal_template = JournalTemplate.objects.create(**validated_data)
        journal_template.category.set(categories)
        self._create_topics_and_prompts(journal_template, topics_data)
        return journal_template

    def update(self, instance, validated_data):
        categories = validated_data.pop('category', None)
        topics_data = validated_data.pop('topics', [])
        tags = validated_data.pop('tags', None)

        #ignore the id if provided
        validated_data.pop('id', None)

        # Update the JournalTemplate fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update categories if provided
        if categories is not None:
            instance.category.set(categories)

        # Update tags if provided
        if tags is not None:
            instance.tags.set(tags)

        # Update topics and prompts
        instance.topics.all().delete()
        for topic_data in topics_data:
            topic_serializer = JournalTopicSerializer(data=topic_data)
            if topic_serializer.is_valid():
                topic_serializer.save(journal=instance)

        return instance

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