# subscriptions/cron.py
app_name = "subscriptions"

from datetime import timedelta

from django.utils import timezone
from django.db.models import Q

from .models import Subscription

def perform_billing():
    now = timezone.now()
    today = now.date()
    due_filters = (
        Q(is_active=True)
        & Q(start_date__isnull=False)
        & Q(end_date__gte=today)
        & Q(last_payment_date__lte=now - timedelta(days=30))
    )

    subscriptions = Subscription.objects.filter(due_filters)
    for subscription in subscriptions:
        try:
            payment_result = subscription.payment()
            subscription.save(update_fields=["last_payment_date", "modified_at"])
            if payment_result:
                try:
                    payment_result.subscription = subscription
                    payment_result.save(update_fields=["subscription", "modified_at"])
                except Exception:
                    pass
        except Exception:
            continue