# subscriptions/tasks.py
app_name = "subscriptions"

from celery import shared_task
from datetime import timedelta

from django.utils import timezone
from django.db.models import Q

from .models import Subscription


from django.core.mail import send_mail

@shared_task
def send_subscription_email(email, text):
    send_mail(
        subject='VAHANA Subscription Request',
        message=f'Your subscription request is: {text}',
        from_email='your_email@gmail.com',
        recipient_list=[email],
        fail_silently=True,
    )    
    return True


@shared_task
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
            subscription.schedule_payment_date = subscription.start_date + timedelta(days=30)
            subscription.save(update_fields=["last_payment_date", "schedule_payment_date", "modified_at"])

            if payment_result:
                payment_result.subscription = subscription
                payment_result.save(update_fields=["subscription", "modified_at"])

        except Exception:
            continue