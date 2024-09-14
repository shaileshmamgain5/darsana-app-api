from rest_framework import serializers
from core.models import MoodEntry, MoodTag, MoodResponse

class MoodTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodTag
        fields = ['id', 'name', 'for_value']

class MoodResponseSerializer(serializers.ModelSerializer):
    mood_tags = MoodTagSerializer(many=True, read_only=True)

    class Meta:
        model = MoodResponse
        fields = ['id', 'mood_tags']

class MoodEntrySerializer(serializers.ModelSerializer):
    responses = MoodResponseSerializer(many=True, read_only=True)
    mood_tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=MoodTag.objects.all(), write_only=True
    )

    class Meta:
        model = MoodEntry
        fields = ['id', 'user', 'created_at', 'mood_value', 'mood_description', 'responses', 'mood_tags']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        mood_tags = validated_data.pop('mood_tags', [])
        mood_entry = MoodEntry.objects.create(**validated_data)
        
        mood_response = MoodResponse.objects.create(mood_entry=mood_entry)
        mood_response.mood_tags.set(mood_tags)
        
        return mood_entry
