# cars/models.py
app_name = 'cars'

from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name="Brand Name")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Brand Slug", null=False, blank=True)
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    image = models.URLField(blank=True, null=True, verbose_name="Brand Image URL")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Modified At")

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"
        ordering = ['name']

    def clean(self):
        super().clean()
        if Brand.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            raise ValidationError({'slug': '동일한 브랜드가 이미 존재합니다.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Model(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models', verbose_name="Brand")
    name = models.CharField(max_length=100, verbose_name="Model Name")
    slug = models.SlugField(max_length=100, verbose_name="Model Slug", null=False, blank=True)
    code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Model Code")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    image = models.URLField(blank=True, null=True, verbose_name="Model Image URL")
    front_image = models.URLField(blank=True, null=True, verbose_name="Model Front Image URL")
    rear_image = models.URLField(blank=True, null=True, verbose_name="Model Rear Image URL")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Modified At")

    class Meta:
        verbose_name = "Model"
        verbose_name_plural = "Models"
        ordering = ['brand', 'name']
        unique_together = [['brand', 'slug']]

    def clean(self):
        super().clean()
        if self.code:
            self.slug = slugify(self.brand.slug + '-' + self.name + '-' + self.code)
        else:
            self.slug = slugify(self.brand.slug + '-' + self.name)

        if Model.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            raise ValidationError({'slug': '동일한 모델이 이미 존재합니다.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand.name} - {self.name} ({self.code})"


class Car(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='cars', verbose_name="Model")
    sub_model = models.CharField(blank=True, null=True, verbose_name="Sub Model")
    trim = models.CharField(blank=True, null=True, verbose_name="Trim")
    color = models.CharField(blank=True, null=True, verbose_name="Color")
    vin_number = models.CharField(max_length=36, unique=True, null=True, verbose_name="VIN Number")
    license_plate = models.CharField(max_length=16, blank=True, null=True, verbose_name="License Plate")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    images = models.JSONField(default=list, blank=True, verbose_name="Images")
    inspection_report = models.URLField(blank=True, null=True, verbose_name="Inspection Report")

    retail_price = models.IntegerField(verbose_name="Retail Price")
    mileage = models.IntegerField(default=0, verbose_name="Mileage")
    release_date = models.DateTimeField(blank=True, null=True, verbose_name="Release Date")

    is_sellable = models.BooleanField(default=True, verbose_name="Is Sellable")
    sell_price = models.IntegerField(blank=True, null=True, verbose_name="Sell Price")

    is_subscriptable = models.BooleanField(default=False, verbose_name="Is Subscriptable")
    subscription_fee_1 = models.IntegerField(blank=True, null=True, verbose_name="Subscription Fee (1 month)")
    subscription_fee_3 = models.IntegerField(blank=True, null=True, verbose_name="Subscription Fee (3 month)")
    subscription_fee_6 = models.IntegerField(blank=True, null=True, verbose_name="Subscription Fee (6 month)")
    subscription_fee_12 = models.IntegerField(blank=True, null=True, verbose_name="Subscription Fee (12 month)")
    subscription_fee_24 = models.IntegerField(blank=True, null=True, verbose_name="Subscription Fee (24 month)")
    subscription_fee_36 = models.IntegerField(blank=True, null=True, verbose_name="Subscription Fee (36 month)")
    subscription_fee_48 = models.IntegerField(blank=True, null=True, verbose_name="Subscription Fee (48 month)")
    subscription_fee_60 = models.IntegerField(blank=True, null=True, verbose_name="Subscription Fee (60 month)")
    subscription_fee_72 = models.IntegerField(blank=True, null=True, verbose_name="Subscription Fee (72 month)")
    subscription_fee_84 = models.IntegerField(blank=True, null=True, verbose_name="Subscription Fee (84 month)")
    subscription_fee_96 = models.IntegerField(blank=True, null=True, verbose_name="Subscription Fee (96 month)")
    subscription_fee_minimum = models.IntegerField(blank=True, null=True, verbose_name="Subscription Fee Minimum")
    subscription_available_from = models.DateField(blank=True, null=True, verbose_name="Subscription Available From")

    is_butler = models.BooleanField(default=False, verbose_name="Is Butler")
    butler_fee = models.IntegerField(blank=True, null=True, verbose_name="Butler Fee")
    butler_overtime_fee = models.IntegerField(blank=True, null=True, verbose_name="Butler Overtime Fee")
    butler_reservated_dates = models.JSONField(blank=True, null=True, verbose_name="Butler Reservated Dates")
    butler_available_from = models.DateField(blank=True, null=True, verbose_name="Butler Available From")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Modified At")
    
    is_new = models.BooleanField(default=True, verbose_name="Is New")
    is_hot = models.BooleanField(default=False, verbose_name="Is Hot")
    
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Car"
        verbose_name_plural = "Cars"
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        if self.is_sellable and not self.sell_price:
            raise ValidationError({'sell_price': '판매 가능한 차량은 판매 가격이 필수입니다.'})

        if self.is_butler and not self.butler_fee:
            raise ValidationError({'butler_price': '버틀러 서비스가 가능한 차량은 버틀러 수수료가 필수입니다.'})

        if self.is_subscriptable:
            self.update_subscription_fee_minimum()
            if not self.subscription_fee_minimum:
                raise ValidationError({'is_subscriptable': '구독 가능한 차량은 최소한 하나의 구독료가 설정되어야 합니다.'})

    def update_subscription_fee_minimum(self):
        subscription_fees = [
            self.subscription_fee_96,
            self.subscription_fee_84,
            self.subscription_fee_72,
            self.subscription_fee_60,
            self.subscription_fee_48,
            self.subscription_fee_36,
            self.subscription_fee_24,
            self.subscription_fee_12,
            self.subscription_fee_6,
            self.subscription_fee_3,
            self.subscription_fee_1,
        ] 
        for fee in subscription_fees:
            if fee is not None and fee > 0:
                self.subscription_fee_minimum = fee
                return 

        self.subscription_fee_minimum = 0

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.model.brand.name} {self.model.name} - {self.sub_model} - {self.license_plate}"