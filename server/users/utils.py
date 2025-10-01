# users/utils.py
app_name = 'users'

from datetime import timedelta

from django.utils import timezone
from django.db import transaction

from subscriptions.models import SubscriptionCoupon, SubscriptionUserCoupon

from .models import Referral, ReferralRule

class ReferralHandler:
    def __init__(self, referrer, referree):
        self.referrer = referrer
        self.referree = referree

    def create(self):
        with transaction.atomic():
            referral_rule = ReferralRule.objects.filter(user=self.referree).first()
            if referral_rule:
                name = referral_rule.name
                description = referral_rule.description
                discount_type = referral_rule.discount_type
                discount_rate = referral_rule.discount_rate
                max_discount = referral_rule.max_discount
                discount = referral_rule.discount
                min_price = referral_rule.min_price
                max_price = referral_rule.max_price
                min_month = referral_rule.min_month
                max_month = referral_rule.max_month
                usage_limit = referral_rule.usage_limit
                usage_limit_per_user = referral_rule.usage_limit_per_user
                valid_from = referral_rule.valid_from
                valid_to = referral_rule.valid_to

                subscription_coupon = SubscriptionCoupon.objects.create(
                    name=name,
                    description=description,
                    discount_type=discount_type,
                    discount_rate=discount_rate,
                    max_discount=max_discount,
                    discount=discount,
                    min_price=min_price,
                    max_price=max_price,
                    min_month=min_month,
                    max_month=max_month,
                    usage_limit=usage_limit,
                    usage_limit_per_user=usage_limit_per_user,
                    valid_from=valid_from,
                    valid_to=valid_to,
                )
                SubscriptionUserCoupon.objects.create(user=self.referrer, coupon=subscription_coupon)
                referral = Referral.objects.create(referrer=self.referrer, referree=self.referree, subscription_coupon=subscription_coupon)
                return referral

            else:
                subscription_coupon = SubscriptionCoupon.objects.create(
                    name=f"추천인 쿠폰",
                    description=f"추천인 쿠폰",
                    discount_type='PERCENTAGE',
                    discount_rate=5,
                    max_discount=700000,
                    usage_limit=2,
                    valid_from=timezone.now(),
                    valid_to=timezone.now() + timedelta(days=30),
                )
                SubscriptionUserCoupon.objects.create(user=self.referrer, coupon=subscription_coupon)
                SubscriptionUserCoupon.objects.create(user=self.referree, coupon=subscription_coupon)
                referral = Referral.objects.create(referrer=self.referrer, referree=self.referree, subscription_coupon=subscription_coupon)
                return referral