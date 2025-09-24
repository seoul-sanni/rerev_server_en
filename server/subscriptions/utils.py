# subscriptions/utils.py
app_name = 'subscriptions'

from datetime import timedelta

from django.db import models
from django.utils import timezone

from cars.models import Car

from .models import Subscription, SubscriptionRequest

def update_subscription_available_from(car_id):
    try:
        car = Car.objects.get(id=car_id)
    except Car.DoesNotExist:
        return
        
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
        car.subscription_available_from = None

    else:
        car.subscription_available_from = latest_end_date + timedelta(days=1)

    car.save()