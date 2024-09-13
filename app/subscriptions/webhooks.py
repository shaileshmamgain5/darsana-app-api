from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .services import SubscriptionService
from core.models import UserSubscription

@csrf_exempt
@require_POST
def google_play_webhook(request):
    # Parse the incoming webhook data
    notification_type = request.POST.get('notificationType')
    purchase_token = request.POST.get('purchaseToken')

    try:
        subscription = UserSubscription.objects.get(receipt_token=purchase_token)
        if notification_type == 'SUBSCRIPTION_RENEWED':
            SubscriptionService.renew_subscription(subscription)
        elif notification_type == 'SUBSCRIPTION_CANCELED':
            SubscriptionService.cancel_subscription(subscription)
        elif notification_type == 'SUBSCRIPTION_EXPIRED':
            SubscriptionService.check_subscription_status(subscription)
    except UserSubscription.DoesNotExist:
        # Handle the case where the subscription is not found
        pass

    return HttpResponse(status=200)

@csrf_exempt
@require_POST
def apple_app_store_webhook(request):
    # Parse the incoming webhook data
    notification_type = request.POST.get('notification_type')
    transaction_id = request.POST.get('transaction_id')

    try:
        subscription = UserSubscription.objects.get(transaction_id=transaction_id)
        if notification_type == 'RENEWAL':
            SubscriptionService.renew_subscription(subscription)
        elif notification_type == 'CANCEL':
            SubscriptionService.cancel_subscription(subscription)
        elif notification_type == 'EXPIRED':
            SubscriptionService.check_subscription_status(subscription)
    except UserSubscription.DoesNotExist:
        # Handle the case where the subscription is not found
        pass

    return HttpResponse(status=200)
