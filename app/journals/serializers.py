from rest_framework import serializers
from core.models import (
    Tag, Category, DayOfWeek, DayOfMonth, JournalTemplate, JournalTopic,
    JournalPrompt, StandalonePrompt, JournalEntry, PromptEntry, Quote, JournalSummary
)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class JournalTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalTemplate
        fields = '__all__'

class JournalTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalTopic
        fields = '__all__'

class JournalPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalPrompt
        fields = '__all__'

class StandalonePromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = StandalonePrompt
        fields = '__all__'

class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = '__all__'

class PromptEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptEntry
        fields = '__all__'

class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = '__all__'

class JournalSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalSummary
        fields = '__all__'
