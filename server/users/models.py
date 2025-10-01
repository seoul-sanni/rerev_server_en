# users/models.py
app_name = 'users'

import random, string

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from accounts.models import User
from subscriptions.models import SubscriptionCoupon

class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals')
    referree = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrees')
    subscription_coupon = models.ForeignKey(SubscriptionCoupon, on_delete=models.CASCADE, null=True, blank=True, related_name='referral_subscription_coupons')

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'
        unique_together = ('referrer', 'referree')

    def __str__(self):
        return f"{self.referrer.username} -> {self.referree.username}"


class ReferralRule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_rules')
    name = models.CharField(max_length=20, verbose_name="Name")
    description = models.TextField(verbose_name="Description")

    discount_type = models.CharField(max_length=20, choices=SubscriptionCoupon.TYPE_CHOICES, default='PERCENTAGE')
    discount_rate = models.IntegerField(verbose_name="Discount Rate", null=True, blank=True)
    max_discount = models.IntegerField(verbose_name="Max Discount Amount", default=700000)
    discount = models.IntegerField(verbose_name="Discount Amount", null=True, blank=True)

    min_price = models.IntegerField(verbose_name="Min Subscription Price", default=0)
    max_price = models.IntegerField(verbose_name="Max Subscription Price", default=1000000000)
    min_month = models.IntegerField(verbose_name="Min Month", default=1)
    max_month = models.IntegerField(verbose_name="Max Month", default=12)

    usage_limit = models.IntegerField(verbose_name="Usage Limit", default=1)
    usage_limit_per_user = models.IntegerField(verbose_name="Usage Limit Per User", default=1)
    valid_from = models.DateTimeField(verbose_name="Valid From", default=timezone.now)
    valid_to = models.DateTimeField(verbose_name="Valid To")

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Referral Rule'
        verbose_name_plural = 'Referral Rules'

    def clean(self):
        # 할인 타입에 따른 필수 필드 검사
        if self.discount_type == 'PERCENTAGE':
            if not self.discount_rate:
                raise ValidationError("퍼센트 할인 타입의 경우 할인율을 입력해야 합니다.")
            if self.discount_rate <= 0 or self.discount_rate > 100:
                raise ValidationError("할인율은 1~100 사이의 값이어야 합니다.")
        elif self.discount_type == 'FIXED':
            if not self.discount:
                raise ValidationError("고정 금액 할인 타입의 경우 할인 금액을 입력해야 합니다.")
            if self.discount <= 0:
                raise ValidationError("할인 금액은 0보다 커야 합니다.")
        elif self.discount_type == 'FREE':
            pass
        
        # 가격 범위 검사
        if self.min_price < 0:
            raise ValidationError("최소 구독 가격은 0 이상이어야 합니다.")
        if self.max_price <= self.min_price:
            raise ValidationError("최대 구독 가격은 최소 구독 가격보다 커야 합니다.")
        
        # 개월 수 범위 검사
        if self.min_month < 1 or self.max_month > 12:
            raise ValidationError("구독 개월 수는 1~12 사이여야 합니다.")
        if self.max_month < self.min_month:
            raise ValidationError("최대 개월 수는 최소 개월 수보다 크거나 같아야 합니다.")

        # 사용 제한 검사
        if self.usage_limit <= 0:
            raise ValidationError("사용 제한은 1 이상이어야 합니다.")
        if self.usage_limit_per_user <= 0:
            raise ValidationError("사용자당 사용 제한은 1 이상이어야 합니다.")

        # 유효기간 검사
        if self.valid_from and self.valid_to and self.valid_from >= self.valid_to:
            raise ValidationError("유효 시작일은 유효 종료일보다 이전이어야 합니다.")
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class PointCoupon(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Code", editable=False)
    name = models.CharField(max_length=20, verbose_name="Name")
    description = models.TextField(verbose_name="Description")

    amount = models.IntegerField(verbose_name="Amount", default=0)

    usage_limit = models.IntegerField(verbose_name="Usage Limit", default=1)                            # Usage Limit
    usage_limit_per_user = models.IntegerField(verbose_name="Usage Limit Per User", default=1)          # Usage Limit Per User

    valid_from = models.DateTimeField(verbose_name="Valid From", default=timezone.now)                  # Valid From
    valid_to = models.DateTimeField(verbose_name="Valid To")                                            # Valid To

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Point Coupon'
        verbose_name_plural = 'Point Coupons'

    def __str__(self):
        return f"{self.name} ({self.code})"

    def generate_code(self):
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(8))
            if not PointCoupon.objects.filter(code=code).exists():
                return code

    def clean(self):
        if self.valid_from and self.valid_to and self.valid_from >= self.valid_to:
            raise ValidationError("유효 시작일은 유효 종료일보다 이전이어야 합니다.")

        # 사용 제한 검사
        if self.usage_limit <= 0:
            raise ValidationError("사용 제한은 1 이상이어야 합니다.")
        if self.usage_limit_per_user <= 0:
            raise ValidationError("사용자당 사용 제한은 1 이상이어야 합니다.")
    
    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.code:
                self.code = self.generate_code()
        
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_valid_now(self):
        now = timezone.now()
        
        # valid_from이 None이거나 valid_to가 None이면 유효하지 않음
        if self.valid_from is None or self.valid_to is None:
            return False
            
        return self.is_active and self.valid_from <= now <= self.valid_to


class PointTransaction(models.Model):
    TYPE_CHOICES = [
        ('COUPON', 'Coupon'),
        ('REFERRAL', 'Referral'),

        ('WITHDRAW', 'Withdraw'),
        ('DEPOSIT', 'Deposit'),

        ('REVIEW', 'Review'),
        ('COMMENT', 'Comment'),
        ('ACTIVITY', 'Activity'),

        ('CANCEL', 'Cancel'),
        ('SERVICE', 'Service'),
        ('OTHER', 'Other'),

        ('SUBSCRIPTION', 'Subscription'),
        ('BUTLER', 'Butler'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    amount = models.IntegerField()
    description = models.TextField(null=True, blank=True)

    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    transaction_id = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Point Transaction'
        verbose_name_plural = 'Point Transactions'

    def save(self, *args, **kwargs):
        if not self.pk:
            points = self.user.point_transactions.filter(is_active=True).aggregate(total=models.Sum('amount'))['total'] or 0
        else:
            points = self.user.point_transactions.filter(is_active=True).exclude(pk=self.pk).aggregate(total=models.Sum('amount'))['total'] or 0

        total_points = points + self.amount
        if total_points < 0:
            raise ValidationError("포인트 잔액이 부족합니다.")

        self.user.point = total_points
        self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.transaction_type} - {self.transaction_id if self.transaction_id else 'None'}"