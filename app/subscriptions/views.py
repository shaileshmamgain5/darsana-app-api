from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import UserSubscription
from .serializers import UserSubscriptionSerializer
from .services import SubscriptionService

# Create your views here.

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserSubscription.objects.filter(user_profile=self.request.user.profile)

    @action(detail=False, methods=['post'])
    def purchase(self, request):
        plan_id = request.data.get('plan_id')
        platform = request.data.get('platform')
        receipt_token = request.data.get('receipt_token')
        transaction_id = request.data.get('transaction_id')

        try:
            subscription = SubscriptionService.purchase_subscription(
                request.user.profile, plan_id, platform, receipt_token, transaction_id
            )
            serializer = self.get_serializer(subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        subscription = self.get_object()
        SubscriptionService.cancel_subscription(subscription)
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        subscription = self.get_object()
        current_status = SubscriptionService.check_subscription_status(subscription)
        return Response({'status': current_status})
