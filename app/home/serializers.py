from rest_framework import serializers
from prompts.serializers import StandalonePromptSerializer
from journals.serializers import JournalEntrySerializer
from goals.serializers import GoalCompletionSerializer
from core.models import Quote


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = ['id', 'text', 'author']

class HomeSerializer(serializers.Serializer):
    date = serializers.DateField()
    morning_intention = JournalEntrySerializer()
    evening_reflection = JournalEntrySerializer()
    goal_completions = GoalCompletionSerializer(many=True)
    prompt_of_the_day = StandalonePromptSerializer()
    quote_of_the_day = QuoteSerializer()
