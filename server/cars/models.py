# cars/models.py
app_name = 'cars'

from datetime import date

from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name="Brand Name")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Brand Slug", null=False, blank=True)
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    image = models.URLField(blank=True, null=True, verbose_name="Brand Image URL")
    is_imported = models.BooleanField(default=False, verbose_name="Is Imported")
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
    FUEL_TYPE_CHOICES = [
        ('GASOLINE', 'Gasoline'),
        ('DIESEL', 'Diesel'),
        ('ELECTRIC', 'Electric'),
        ('HYBRID', 'Hybrid'),
        ('LPG', 'LPG'),
    ]

    TRANSMISSION_TYPE_CHOICES = [
        ('MANUAL', 'Manual'),
        ('AUTOMATIC', 'Automatic'),
    ]

    DRIVE_TYPE_CHOICES = [
        ('FWD', 'Front Wheel Drive'),
        ('RWD', 'Rear Wheel Drive'),
        ('AWD', 'All Wheel Drive'),
    ]

    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='cars', verbose_name="Model")
    sub_model = models.CharField(blank=True, null=True, verbose_name="Sub Model")
    engine_size = models.IntegerField(verbose_name="Engine Size", default=2000)
    fuel_type = models.CharField(verbose_name="Fuel Type", choices=FUEL_TYPE_CHOICES, default='GASOLINE')
    transmission_type = models.CharField(verbose_name="Transmission Type", choices=TRANSMISSION_TYPE_CHOICES, default='AUTOMATIC')
    drive_type = models.CharField(verbose_name="Drive Type", choices=DRIVE_TYPE_CHOICES, default='FWD')
    passenger_count = models.IntegerField(verbose_name="Passenger Count", default=5)
    trim = models.CharField(blank=True, null=True, verbose_name="Trim")
    color = models.CharField(blank=True, null=True, verbose_name="Color")
    vin_number = models.CharField(max_length=36, unique=True, null=True, verbose_name="VIN Number")
    license_plate = models.CharField(max_length=16, blank=True, null=True, verbose_name="License Plate")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    images = models.JSONField(default=list, blank=True, verbose_name="Images")
    inspection_report = models.URLField(blank=True, null=True, verbose_name="Inspection Report")

    retail_price = models.IntegerField(verbose_name="Retail Price")
    release_date = models.DateField(blank=True, null=True, verbose_name="Release Date")
    tax = models.IntegerField(blank=True, null=True, verbose_name="Tax")
    acquisition_tax = models.IntegerField(blank=True, null=True, verbose_name="Acquisition Tax")
    mileage = models.IntegerField(default=0, verbose_name="Mileage")

    is_sellable = models.BooleanField(default=False, verbose_name="Is Sellable")
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
    subscription_overmileage_fee = models.IntegerField(blank=True, null=True, verbose_name="Subscription Overmileage Fee")
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

    def calculate_car_age(self):
        if not self.release_date:
            return 1
        today = date.today()
        age = today.year - self.release_date.year
        if today.month < self.release_date.month or (today.month == self.release_date.month and today.day < self.release_date.day):
            age -= 1
        return max(1, age)
    
    def calculate_tax(self):
        if self.fuel_type == 'ELECTRIC':
            return 260000

        if self.engine_size <= 1000:
            base_tax = self.engine_size * 80 * 1.3
        elif self.engine_size <= 1600:
            base_tax = self.engine_size * 140 * 1.3
        else:
            base_tax = self.engine_size * 200 * 1.3
        age = self.calculate_car_age()
        discount_table = {1: 1.0, 2: 1.0, 3: 0.95, 4: 0.90, 5: 0.85, 6: 0.80, 7: 0.75, 8: 0.70, 9: 0.65, 10: 0.60, 11: 0.55, 12: 0.50}
        age = min(age, 12)
        return int(base_tax * discount_table[age])
    
    def calculate_acquisition_tax(self):
        age = self.calculate_car_age()
        if self.model.brand.is_imported:
            discount_table = {1: 0.729, 2: 0.605, 3: 0.5, 4: 0.412, 5: 0.34, 6: 0.281, 7: 0.232, 8: 0.172, 9: 0.142, 10: 0.117, 11: 0.097, 12: 0.08, 13:0.066, 14:0.054, 15:0.05, 16:0.048, 17:0.046, 18:0.044, 19:0.042, 20:0.04}
        else:
            discount_table = {1: 0.725, 2: 0.614, 3: 0.518, 4: 0.437, 5: 0.368, 6: 0.311, 7: 0.262, 8: 0.221, 9: 0.186, 10: 0.157, 11: 0.132, 12: 0.112, 13: 0.094, 14: 0.079, 15: 0.067, 16: 0.063, 17: 0.06, 18: 0.057, 19: 0.053, 20: 0.05}
        age = min(age, 20)
        return int(self.retail_price * discount_table[age] * 0.07)

    def save(self, *args, **kwargs):
        self.tax = self.calculate_tax()
        self.acquisition_tax = self.calculate_acquisition_tax()
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.model.brand.name} {self.model.name} - {self.sub_model} - {self.license_plate}"