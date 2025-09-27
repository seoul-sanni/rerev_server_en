# butlers/models.py
app_name = 'butlers'

import random, string

from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from accounts.models import User
from cars.models import Car, Model

class ButlerCoupon(models.Model):
    TYPE_CHOICES = [
        ('PERCENTAGE', 'Percentage'),
        ('FIXED', 'Fixed'),
        ('FREE', 'Free'),
    ]

    code = models.CharField(max_length=20, unique=True, verbose_name="Code", editable=False)
    name = models.CharField(max_length=20, verbose_name="Name")
    description = models.TextField(verbose_name="Description")

    brand_ids = models.JSONField(verbose_name="Brand IDs", default=list, blank=True)
    model_ids = models.JSONField(verbose_name="Model IDs", default=list, blank=True)
    car_ids = models.JSONField(verbose_name="Car IDs", default=list, blank=True)

    discount_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='PERCENTAGE')         # Discount Type
    discount_rate = models.IntegerField(verbose_name="Discount Rate", null=True, blank=True)            # Discount Rate (Percentage)
    max_discount = models.IntegerField(verbose_name="Max Discount Amount", default=1000000000)          # Max Discount Amount (Percentage)
    discount = models.IntegerField(verbose_name="Discount Amount", null=True, blank=True)               # Discount Amount (Fixed)

    min_price = models.IntegerField(verbose_name="Min Buttler Price", default=0)                        # Min Buttler Price
    max_price = models.IntegerField(verbose_name="Max Buttler Price", default=1000000000)               # Max Buttler Price

    usage_limit = models.IntegerField(verbose_name="Usage Limit", default=1)                            # Usage Limit
    usage_limit_per_user = models.IntegerField(verbose_name="Usage Limit Per User", default=1)          # Usage Limit Per User

    valid_from = models.DateTimeField(verbose_name="Valid From", default=timezone.now)                  # Valid From
    valid_to = models.DateTimeField(verbose_name="Valid To")                                            # Valid To

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def generate_code(self):
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(8))
            if not ButlerCoupon.objects.filter(code=code).exists():
                return code

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
        
        # 유효기간 검사
        if self.valid_from and self.valid_to and self.valid_from >= self.valid_to:
            raise ValidationError("유효 시작일은 유효 종료일보다 이전이어야 합니다.")
        
        # 사용 제한 검사
        if self.usage_limit <= 0:
            raise ValidationError("사용 제한은 1 이상이어야 합니다.")
        if self.usage_limit_per_user <= 0:
            raise ValidationError("사용자당 사용 제한은 1 이상이어야 합니다.")
        
        # 가격 범위 검사
        if self.min_price < 0:
            raise ValidationError("최소 구독 가격은 0 이상이어야 합니다.")
        if self.max_price <= self.min_price:
            raise ValidationError("최대 구독 가격은 최소 구독 가격보다 커야 합니다.")

    def save(self, *args, **kwargs):
        # 새로 생성되는 경우에만 기본값 설정
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
            
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_to
        )
    
    @property
    def discount_amount(self):
        if self.discount_type == 'PERCENTAGE':
            return f"{self.discount_rate}%"
        elif self.discount_type == 'FIXED':
            return f"{self.discount:,}원"
        elif self.discount_type == 'FREE':
            return "무료"
        return "할인 없음"
    
    @property
    def is_specific(self):
        if not self.brand_ids and not self.model_ids and not self.car_ids:
            return False
        
        return True


class ButlerUserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='butler_user_coupons')
    coupon = models.ForeignKey(ButlerCoupon, on_delete=models.CASCADE, related_name='butler_user_coupons')

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    used_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Butler User Coupon"
        verbose_name_plural = "Butler User Coupons"

    def __str__(self):
        if self.coupon.discount_type == 'PERCENTAGE':
            return f"{self.user.email}-{self.coupon.name}-{self.coupon.discount_type}-{self.coupon.discount_rate}%"
        elif self.coupon.discount_type == 'FIXED':
            return f"{self.user.email}-{self.coupon.name}-{self.coupon.discount_type}-{self.coupon.discount}원"
        elif self.coupon.discount_type == 'FREE':
            return f"{self.user.email}-{self.coupon.name}-{self.coupon.discount_type}"

    @property
    def is_used(self):
        return self.used_at is not None

    @property
    def is_valid(self):
        if not self.is_active or self.is_used:
            return False
        return self.coupon.is_valid_now

    def use_coupon(self):
        if not self.is_valid:
            raise ValueError("사용할 수 없는 쿠폰입니다.")
        
        self.used_at = timezone.now()
        self.save()

    def return_coupon(self):
        self.used_at = None
        self.save()

    def clean(self):
        # 쿠폰이 존재하는지 확인
        if not self.coupon:
            raise ValidationError("쿠폰을 선택해야 합니다.")
        
        # 사용자가 존재하는지 확인
        if not self.user:
            raise ValidationError("사용자를 선택해야 합니다.")
        
        # 이미 같은 사용자가 같은 쿠폰을 가지고 있는지 확인 (새로 생성되는 경우에만)
        if self.pk is None:  # 새로 생성되는 경우에만
            if ButlerUserCoupon.objects.filter(user=self.user, coupon=self.coupon, used_at=None).exists():
                raise ValidationError("이미 해당 쿠폰을 보유하고 있습니다.")
        
        # 쿠폰의 전체 사용 제한 확인 (현재 레코드 제외)
        used_count = ButlerUserCoupon.objects.filter(
            coupon=self.coupon,
        ).exclude(pk=self.pk).count()
        
        if used_count >= self.coupon.usage_limit:
            raise ValidationError(f"이 쿠폰은 이미 최대 사용 횟수({self.coupon.usage_limit}회)에 도달했습니다.")
        
        # 사용자당 사용 제한 확인 (현재 레코드 제외)
        user_used_count = ButlerUserCoupon.objects.filter(
            user=self.user,
            coupon=self.coupon,
        ).exclude(pk=self.pk).count()
        
        if user_used_count >= self.coupon.usage_limit_per_user:
            raise ValidationError(f"이 쿠폰은 사용자당 최대 {self.coupon.usage_limit_per_user}회까지 사용할 수 있습니다.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ButlerRequest(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='butler_requests')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='butler_requests')

    start_at = models.DateTimeField(verbose_name="Start At", null=True, blank=True)
    start_location = models.CharField(max_length=255, verbose_name="Start Location")
    end_at = models.DateTimeField(verbose_name="End At", null=True, blank=True)
    end_location = models.CharField(max_length=255, verbose_name="End Location")

    coupon = models.ForeignKey(ButlerUserCoupon, on_delete=models.CASCADE, related_name='butler_requests', null=True, blank=True)
    point = models.ForeignKey('users.PointTransaction', on_delete=models.CASCADE, related_name='butler_requests', null=True, blank=True)

    payment_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Butler Request"
        verbose_name_plural = "Butler Requests"
        unique_together = [('user', 'coupon'), ('user', 'point')]

    def clean(self):
        if self.coupon:
            if self.coupon.user != self.user:
                raise ValidationError("쿠폰의 소유자와 요청자가 다릅니다.")
    
    def save(self, *args, **kwargs):
        if not self.start_at:
            self.start_at = timezone.now()
        
        if not self.end_at:
            self.end_at = self.start_at + timedelta(hours=10)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.name} - {self.start_location} {self.start_at} ~ {self.end_location} {self.end_at} - {self.car.model.brand.name} {self.car.model.name})"


class ButlerWayPoint(models.Model):
    butler_request = models.ForeignKey(ButlerRequest, on_delete=models.CASCADE, related_name='butler_way_points')
    address = models.CharField(max_length=255)
    scheduled_time = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Butler Way Point"
        verbose_name_plural = "Butler Way Points"


class Butler(models.Model):
    request = models.ForeignKey(ButlerRequest, on_delete=models.CASCADE, related_name='butlers')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Modified At")

    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    
    class Meta:
        verbose_name = "Butler"
        verbose_name_plural = "Butlers"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.request.user.username} - {self.request.car.model.brand.name} {self.request.car.model.name} ({self.request.start_at} ~ {self.request.end_at})"


class ButlerLike(models.Model):
    id = models.AutoField(primary_key=True)
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='butler_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='butler_likes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('model', 'user')  # 유저당 한 모델에 한 번만 좋아요
        verbose_name = "Like"
        verbose_name_plural = "Likes"
    
    def __str__(self):
        return f"{self.user.username} likes {self.model.brand.name} {self.model.name}"
    

class ButlerReview(models.Model):
    id = models.AutoField(primary_key=True)
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='butler_reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='butler_reviews')

    content = models.TextField()
    image = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.model.brand.name} {self.model.name}"
    
    def soft_delete(self):
        self.is_active = False
        self.content = "삭제된 리뷰입니다."
        self.save()

    class Meta:
        verbose_name_plural = "Reviews"
        ordering = ['-id']


class ButlerReviewLike(models.Model):
    id = models.AutoField(primary_key=True)
    review = models.ForeignKey(ButlerReview, on_delete=models.CASCADE, related_name='butler_review_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='butler_review_likes')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')  # 유저당 한 리뷰에 한 번만 좋아요
        verbose_name = "Review Like"
        verbose_name_plural = "Review Likes"

    def __str__(self):
        return f"{self.user.username} likes Review {self.review.id}"


class ButlerModelRequest(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='butler_model_requests')
    model = models.TextField(verbose_name="Model")

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Model Request"
        verbose_name_plural = "Model Requests"