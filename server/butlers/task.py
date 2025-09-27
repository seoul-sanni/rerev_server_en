# butlers/task.py
app_name = "butlers"

from celery import shared_task

from django.core.mail import send_mail

@shared_task
def send_butler_email(email, text):
    send_mail(
        subject='VAHANA Butler Request',
        message=f'Your butler request is: {text}',
        from_email='your_email@gmail.com',
        recipient_list=[email],
        fail_silently=True,
    )    
    return True
