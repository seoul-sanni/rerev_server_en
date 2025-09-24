# subscriptions/signals.py
app_name = "subscriptions"

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from .models import SubscriptionRequest, Subscription
from .utils import update_subscription_available_from

# Subscription Request
# <-------------------------------------------------------------------------------------------------------------------------------->
@receiver(pre_save, sender=SubscriptionRequest)
def handle_coupon_removal(sender, instance, **kwargs):
    if instance.pk:
        old_instance = SubscriptionRequest.objects.get(pk=instance.pk)
        if old_instance.coupon:
            old_instance.coupon.return_coupon()


@receiver(pre_save, sender=SubscriptionRequest)
def handle_point_removal(sender, instance, **kwargs):
    if instance.pk:
        old_instance = SubscriptionRequest.objects.get(pk=instance.pk)
        old_point = old_instance.point
        if old_point and instance.point != old_point:
            old_point.delete()


@receiver(post_save, sender=SubscriptionRequest)
def handle_coupon_use(sender, instance, **kwargs):
    if instance.coupon:
        def use_coupon_after_commit():
            instance.coupon.refresh_from_db()
            instance.coupon.use_coupon()
        transaction.on_commit(use_coupon_after_commit)


@receiver(post_save, sender=SubscriptionRequest)
def handle_point_transaction(sender, instance, **kwargs):
    if instance.point:
        instance.point.transaction_type = 'SUBSCRIPTION'
        instance.point.transaction_id = instance.id
        instance.point.save()


@receiver(post_save, sender=SubscriptionRequest)
def update_car_available_from_on_request_save(sender, instance, **kwargs):
    update_subscription_available_from(instance.car.id)


@receiver(post_delete, sender=SubscriptionRequest)
def return_coupon_on_delete(sender, instance, **kwargs):
    if instance.coupon:
        instance.coupon.return_coupon()


@receiver(post_delete, sender=SubscriptionRequest)
def return_point_on_delete(sender, instance, **kwargs):
    if instance.point:
        instance.point.delete()


@receiver(post_delete, sender=SubscriptionRequest)
def update_car_available_from_on_request_delete(sender, instance, **kwargs):
    update_subscription_available_from(instance.car.id)


# Subscription
# <-------------------------------------------------------------------------------------------------------------------------------->
@receiver(pre_save, sender=Subscription)
def handle_request_activation(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Subscription.objects.get(pk=instance.pk)
        if old_instance.request:
            old_instance.request.is_active = True
            old_instance.request.save()


@receiver(post_save, sender=Subscription)
def handle_request_inactivation(sender, instance, **kwargs):
    if instance.request:
        def inactivate_request_after_commit():
            instance.request.is_active = False
            instance.request.save()
        transaction.on_commit(inactivate_request_after_commit)


@receiver(post_save, sender=Subscription)
def update_car_available_from_on_subscription_save(sender, instance, **kwargs):
    update_subscription_available_from(instance.request.car.id)


@receiver(post_delete, sender=Subscription)
def update_car_available_from_on_subscription_delete(sender, instance, **kwargs):
    update_subscription_available_from(instance.request.car.id)