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
        & Q(schedule_payment_date__lte=today)
    )

    subscriptions = Subscription.objects.filter(due_filters)
    for subscription in subscriptions:
        try:
            payment_result = subscription.payment()
            subscription.schedule_payment_date = subscription.start_date + timedelta(days=31)
            subscription.save(update_fields=["last_payment_date", "schedule_payment_date", "modified_at"])

            if payment_result:
                payment_result.subscription = subscription
                payment_result.save(update_fields=["subscription", "modified_at"])

        except Exception:
            continue