from rest_framework import serializers
from core.models import Profile, JournalTemplate

class JournalTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalTemplate
        fields = ['id', 'title']

class ProfileSerializer(serializers.ModelSerializer):
    morning_intention = JournalTemplateSerializer(read_only=True)
    evening_reflection = JournalTemplateSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['name', 'email', 'subscription_details', 'morning_intention', 
                  'evening_reflection', 'theme', 'day_start', 'day_end', 
                  'week_start', 'model_imagination']
        read_only_fields = ['email', 'subscription_details']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
