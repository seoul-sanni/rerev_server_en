# subscriptions/utils.py
app_name = 'subscriptions'

from datetime import timedelta

from django.db import models
from django.utils import timezone

from .models import Subscription, SubscriptionRequest

def get_subscription_available_from(car):
    now = timezone.now().date()
    latest_end_date = None
    
    subscriptions = Subscription.objects.filter(request__car=car, end_date__gte=now)
    if subscriptions.exists():
        latest_subscription_end = subscriptions.aggregate(max_end=models.Max('end_date'))['max_end']
        if latest_subscription_end:
            latest_end_date = latest_subscription_end
    
    subscription_requests = SubscriptionRequest.objects.filter(car=car, end_date__gte=now, is_active=True)
    if subscription_requests.exists():
        latest_request_end = subscription_requests.aggregate(max_end=models.Max('end_date'))['max_end']
        if latest_request_end:
            if latest_end_date is None or latest_request_end > latest_end_date:
                latest_end_date = latest_request_end
    
    if latest_end_date is None:
        subscription_available_from = None

    else:
        subscription_available_from = latest_end_date + timedelta(days=1)

    return subscription_available_from