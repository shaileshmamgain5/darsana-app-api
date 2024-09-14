from rest_framework import serializers
from core.models import Profile, JournalTemplate

class JournalTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalTemplate
        fields = ['id', 'title']

class ProfileSerializer(serializers.ModelSerializer):
    morning_intention = JournalTemplateSerializer(read_only=True)
    evening_reflection = JournalTemplateSerializer(read_only=True)
    morning_intention_id = serializers.PrimaryKeyRelatedField(
        queryset=JournalTemplate.objects.all(),
        source='morning_intention',
        write_only=True,
        required=False,
        allow_null=True
    )
    evening_reflection_id = serializers.PrimaryKeyRelatedField(
        queryset=JournalTemplate.objects.all(),
        source='evening_reflection',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Profile
        fields = ['name', 'email', 'subscription_details', 'morning_intention', 
                  'evening_reflection', 'morning_intention_id', 'evening_reflection_id',
                  'theme', 'day_start', 'day_end', 'week_start', 'model_imagination']
        read_only_fields = ['email', 'subscription_details']

    def update(self, instance, validated_data):
        morning_intention = validated_data.pop('morning_intention', None)
        evening_reflection = validated_data.pop('evening_reflection', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if morning_intention is not None:
            instance.morning_intention = morning_intention
        if evening_reflection is not None:
            instance.evening_reflection = evening_reflection

        instance.save()
        return instance

    def validate_morning_intention_id(self, value):
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("Invalid morning intention template.")
        return value

    def validate_evening_reflection_id(self, value):
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("Invalid evening reflection template.")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['email'] = instance.user.email
        return representation
