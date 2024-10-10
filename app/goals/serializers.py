from rest_framework import serializers
from core.models import Goal, GoalRepetition, GoalCompletion, DayOfWeek, DayOfMonth

class DayOfWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayOfWeek
        fields = ['id', 'day']

class DayOfMonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayOfMonth
        fields = ['id', 'day']

class GoalRepetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalRepetition
        fields = ['id', 'repeat_on', 'frequency']

class GoalCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalCompletion
        fields = ['id', 'date', 'is_completed']

class GoalSerializer(serializers.ModelSerializer):
    repetition = GoalRepetitionSerializer(required=False)
    completions = GoalCompletionSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'start_date', 'end_date', 'repeat_type', 'is_active', 'progress', 'repetition', 'completions']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        repetition_data = validated_data.pop('repetition', None)
        goal = Goal.objects.create(**validated_data)

        if repetition_data:
            GoalRepetition.objects.create(goal=goal, **repetition_data)

        return goal

    def update(self, instance, validated_data):
        repetition_data = validated_data.pop('repetition', None)
        instance = super().update(instance, validated_data)

        if repetition_data:
            GoalRepetition.objects.update_or_create(
                goal=instance,
                defaults=repetition_data
            )

        return instance
