from rest_framework import serializers
from core.models import AppConfiguration

class AppConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppConfiguration
        fields = ['id', 'version', 'is_active', 'configurations', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
