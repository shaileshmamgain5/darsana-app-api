from rest_framework import serializers
from core.models import UserSubscription, SubscriptionPlan

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'platform', 'price', 'duration_days', 'description']

class UserSubscriptionSerializer(serializers.ModelSerializer):
    subscription_plan = SubscriptionPlanSerializer(read_only=True)
    status = serializers.CharField(read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = ['id', 'subscription_plan', 'start_date', 'end_date', 'status', 'is_active']

    def get_is_active(self, obj):
        return obj.is_active()
