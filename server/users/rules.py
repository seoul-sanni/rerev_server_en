# users/rules.py
app_name = 'users'

from django.utils import timezone
from datetime import timedelta

from subscriptions.models import SubscriptionCoupon, SubscriptionUserCoupon

from .models import Referral

class RefferalRule:
    def __init__(self, referrer, referree):
        self.referrer = referrer
        self.referree = referree

    def create(self):
        subscription_coupon = SubscriptionCoupon.objects.create(
            name=f"추천인 쿠폰",
            description=f"추천인 쿠폰",
            discount_type='PERCENTAGE',
            discount_rate=50,
            max_discount=700000,
            usage_limit=2,
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30),
        )
        SubscriptionUserCoupon.objects.create(user=self.referrer, coupon=subscription_coupon)
        SubscriptionUserCoupon.objects.create(user=self.referree, coupon=subscription_coupon)
        referral = Referral.objects.create(referrer=self.referrer, referree=self.referree, subscription_coupon=subscription_coupon)
        return referral
