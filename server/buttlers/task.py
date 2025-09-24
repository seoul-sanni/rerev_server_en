# buttlers/task.py
app_name = "buttlers"

from celery import shared_task

from django.core.mail import send_mail

@shared_task
def send_buttler_email(email, text):
    send_mail(
        subject='VAHANA Buttler Request',
        message=f'Your buttler request is: {text}',
        from_email='your_email@gmail.com',
        recipient_list=[email],
        fail_silently=True,
    )    
    return True
