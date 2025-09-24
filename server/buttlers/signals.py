# subscriptions/signals.py
app_name = "buttlers"

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from .models import Buttler, ButtlerRequest

@receiver(pre_save, sender=ButtlerRequest)
def handle_coupon_removal(sender, instance, **kwargs):
    if instance.pk:
        old_instance = ButtlerRequest.objects.get(pk=instance.pk)
        if old_instance.coupon:
            old_instance.coupon.return_coupon()


@receiver(pre_save, sender=ButtlerRequest)
def handle_point_removal(sender, instance, **kwargs):
    if instance.pk:
        old_instance = ButtlerRequest.objects.get(pk=instance.pk)
        old_point = old_instance.point
        if old_point and instance.point != old_point:
            old_point.delete()


@receiver(post_save, sender=ButtlerRequest)
def handle_coupon_use(sender, instance, **kwargs):
    if instance.coupon:
        def use_coupon_after_commit():
            instance.coupon.refresh_from_db()
            instance.coupon.use_coupon()
        transaction.on_commit(use_coupon_after_commit)


@receiver(post_save, sender=ButtlerRequest)
def handle_point_transaction(sender, instance, **kwargs):
    if instance.point:
        instance.point.transaction_type = 'BUTTLER'
        instance.point.transaction_id = instance.id
        instance.point.save()


@receiver(post_delete, sender=ButtlerRequest)
def return_coupon_on_delete(sender, instance, **kwargs):
    if instance.coupon:
        instance.coupon.return_coupon()


@receiver(post_delete, sender=ButtlerRequest)
def return_point_on_delete(sender, instance, **kwargs):
    if instance.point:
        instance.point.delete()


@receiver(pre_save, sender=Buttler)
def handle_request_activation(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Buttler.objects.get(pk=instance.pk)
        if old_instance.request:
            old_instance.request.is_active = True
            old_instance.request.save()


@receiver(post_save, sender=Buttler)
def handle_request_activation(sender, instance, **kwargs):
    if instance.request:
        def activate_request_after_commit():
            instance.request.is_active = False
            instance.request.save()
        transaction.on_commit(activate_request_after_commit)