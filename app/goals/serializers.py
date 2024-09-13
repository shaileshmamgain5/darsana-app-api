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
    days_of_week = DayOfWeekSerializer(many=True, required=False)
    days_of_month = DayOfMonthSerializer(many=True, required=False)

    class Meta:
        model = GoalRepetition
        fields = ['id', 'repeat_type', 'days_of_week', 'days_of_month', 'last_day_of_month']

class GoalCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalCompletion
        fields = ['id', 'date', 'is_completed']

class GoalSerializer(serializers.ModelSerializer):
    repetitions = GoalRepetitionSerializer(many=True, required=False)
    completions = GoalCompletionSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'repeats', 'is_active', 'repetitions', 'completions']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        repetitions_data = validated_data.pop('repetitions', [])
        goal = Goal.objects.create(**validated_data)

        for repetition_data in repetitions_data:
            days_of_week_data = repetition_data.pop('days_of_week', [])
            days_of_month_data = repetition_data.pop('days_of_month', [])
            repetition = GoalRepetition.objects.create(goal=goal, **repetition_data)
            repetition.days_of_week.set(days_of_week_data)
            repetition.days_of_month.set(days_of_month_data)

        return goal

    def update(self, instance, validated_data):
        repetitions_data = validated_data.pop('repetitions', [])
        instance = super().update(instance, validated_data)

        instance.repetitions.all().delete()
        for repetition_data in repetitions_data:
            days_of_week_data = repetition_data.pop('days_of_week', [])
            days_of_month_data = repetition_data.pop('days_of_month', [])
            repetition = GoalRepetition.objects.create(goal=instance, **repetition_data)
            repetition.days_of_week.set(days_of_week_data)
            repetition.days_of_month.set(days_of_month_data)

        return instance
