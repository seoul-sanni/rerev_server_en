# subscriptions/task.py
app_name = "subscriptions"

from celery import shared_task

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
