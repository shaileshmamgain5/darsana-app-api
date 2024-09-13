from django.utils import timezone
from core.models import UserSubscription, SubscriptionPlan

class SubscriptionService:
    @staticmethod
    def purchase_subscription(user_profile, plan_id, platform, receipt_token, transaction_id):
        plan = SubscriptionPlan.objects.get(id=plan_id)
        end_date = timezone.now().date() + timezone.timedelta(days=plan.duration_days)
        
        subscription, created = UserSubscription.objects.update_or_create(
            user_profile=user_profile,
            defaults={
                'subscription_plan': plan,
                'start_date': timezone.now().date(),
                'end_date': end_date,
                'status': 'active',
                'receipt_token': receipt_token,
                'transaction_id': transaction_id
            }
        )
        return subscription

    @staticmethod
    def renew_subscription(subscription):
        if subscription.subscription_plan:
            subscription.start_date = timezone.now().date()
            subscription.end_date = subscription.start_date + timezone.timedelta(days=subscription.subscription_plan.duration_days)
            subscription.status = 'active'
            subscription.save()
        return subscription

    @staticmethod
    def cancel_subscription(subscription):
        subscription.status = 'canceled'
        subscription.save()
        return subscription

    @staticmethod
    def check_subscription_status(subscription):
        if subscription.end_date and subscription.end_date <= timezone.now().date():
            subscription.status = 'expired'
            subscription.save()
        return subscription.status
