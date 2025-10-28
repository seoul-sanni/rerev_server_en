# subscriptions/serializers.py
app_name = 'subscriptions'

from rest_framework import serializers

from cars.models import Brand, Model, Car
from users.models import PointTransaction
from payments.utils import create_toss_billing, create_portone_billing, confirm_toss_payment
from payments.serializers import BillingSerializer, PaymentSerializer
from accounts.models import User

from .models import Subscription, SubscriptionRequest, SubscriptionReview, SubscriptionModelRequest, SubscriptionCoupon, SubscriptionUserCoupon

# Default Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class SubscriptionBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'is_imported', 'image']


class SimpleSubscriptionModelSerializer(serializers.ModelSerializer):
    car_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Model
        fields = ['id', 'name', 'image', 'front_image', 'rear_image', 'code', 'slug', 'car_count']
    
    def get_car_count(self, obj):
        return obj.cars.filter(is_active=True, is_subscriptable=True).count()


class SubscriptionModelSerializer(SimpleSubscriptionModelSerializer):
    brand = SubscriptionBrandSerializer(read_only=True)

    class Meta:
        model = Model
        fields = ['id', 'brand', 'name', 'code', 'image', 'front_image', 'rear_image', 'slug']


# Car Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class SimpleSubscriptionCarSerializer(serializers.ModelSerializer):
    model = SubscriptionModelSerializer(read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'model', 'sub_model', 'engine_size', 'fuel_type', 'transmission_type', 'drive_type', 'passenger_count', 'trim', 'color', 'vin_number', 'license_plate', 'description', 'images', 'inspection_report', 'retail_price', 'release_date', 'tax', 'acquisition_tax', 'mileage', 'is_new', 'is_hot',
        'is_sellable', 'sell_price',
        'is_subscriptable', 'subscription_fee_1', 'subscription_fee_3', 'subscription_fee_6', 'subscription_fee_12', 'subscription_fee_24',
        'subscription_fee_36', 'subscription_fee_48', 'subscription_fee_60', 'subscription_fee_72', 'subscription_fee_84', 'subscription_fee_96',
        'subscription_overmileage_fee', 'subscription_fee_minimum', 'subscription_available_from'
        ]


class SubscriptionCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'sub_model', 'engine_size', 'fuel_type', 'transmission_type', 'drive_type', 'passenger_count', 'trim', 'color', 'vin_number', 'license_plate', 'description', 'images', 'inspection_report', 'retail_price', 'release_date', 'tax', 'acquisition_tax', 'mileage', 'is_new', 'is_hot',
        'is_sellable', 'sell_price',
        'is_subscriptable', 'subscription_fee_1', 'subscription_fee_3', 'subscription_fee_6', 'subscription_fee_12', 'subscription_fee_24',
        'subscription_fee_36', 'subscription_fee_48', 'subscription_fee_60', 'subscription_fee_72', 'subscription_fee_84', 'subscription_fee_96',
        'subscription_overmileage_fee', 'subscription_fee_minimum', 'subscription_available_from'
        ]


class SubscriptionCarDetailSerializer(SubscriptionCarSerializer):
    model = SubscriptionModelSerializer(read_only=True)
    
    class Meta:
        model = Car
        fields = SubscriptionCarSerializer.Meta.fields + ['model']


# Model Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class SubscriptionModelListSerializer(serializers.ModelSerializer):
    brand = SubscriptionBrandSerializer(read_only=True)
    car = serializers.SerializerMethodField()
    
    class Meta:
        model = Model
        fields = ['id', 'brand', 'name', 'code', 'image', 'car']
    
    def get_car(self, obj):
        cars = list(obj.cars.all())
        
        if cars:
            return self.get_car_serializer()(cars, many=True).data
        return None
    
    def get_car_serializer(self):
        return SubscriptionCarSerializer


class SubscriptionModelDetailSerializer(SubscriptionModelListSerializer):
    def get_car_serializer(self):
        return SubscriptionCarSerializer


# Coupon Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class SubscriptionCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionCoupon
        fields = ['id', 'code', 'name', 'description', 'brand_ids', 'model_ids', 'car_ids', 'discount_type', 'discount_rate', 'max_discount', 'discount', 'min_price', 'max_price', 'min_month', 'max_month', 'valid_from', 'valid_to', 'is_specific']
        read_only_fields = ['id', 'code', 'created_at', 'modified_at']


class SubscriptionUserCouponSerializer(serializers.ModelSerializer):
    coupon = SubscriptionCouponSerializer(read_only=True)

    class Meta:
        model = SubscriptionUserCoupon
        fields = ['id', 'user', 'coupon', 'is_active', 'is_used', 'is_valid', 'created_at', 'used_at']
        read_only_fields = ['id', 'user', 'coupon', 'is_used', 'is_valid', 'created_at', 'modified_at', 'used_at']


# Subscription Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class SubscriptionRequestSerializer(serializers.ModelSerializer):
    car = SimpleSubscriptionCarSerializer(read_only=True)
    coupon_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    coupon = SubscriptionUserCouponSerializer(read_only=True)
    point_amount = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    point_used = serializers.SerializerMethodField(read_only=True)
    customer_key = serializers.CharField(write_only=True, required=False, allow_null=True)
    auth_key = serializers.CharField(write_only=True, required=False, allow_null=True)
    billing_key = serializers.CharField(write_only=True, required=False, allow_null=True)
    billing = BillingSerializer(read_only=True)
    payment_key = serializers.CharField(write_only=True, required=False, allow_null=True)
    payment = PaymentSerializer(read_only=True)
    order_id = serializers.CharField(write_only=True, required=False, allow_null=True)
    exchange_rate = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = SubscriptionRequest
        fields = [
            'id', 'user', 'car', 'month', 'start_date', 'end_date', 'point_used', 'created_at', 'modified_at', 'coupon_id', 'coupon', 'is_active', 'point_amount',
            'customer_key', 'auth_key', 'billing_key', 'billing',
            'payment_key', 'payment', 'order_id', 'exchange_rate'
        ]
        read_only_fields = ['id', 'user', 'car', 'point_used', 'end_date', 'created_at', 'modified_at', 'coupon', 'billing', 'payment', 'is_active']
    
    def get_point_used(self, obj):
        if obj.point:
            return -obj.point.amount
        return None
    
    def create(self, validated_data):
        # Billing
        user = validated_data.get('user')
        auth_key = validated_data.pop('auth_key', None)
        customer_key = validated_data.pop('customer_key', None)
        billing_key = validated_data.pop('billing_key', None)
        if auth_key and customer_key:
            billing = create_toss_billing(user, auth_key, customer_key)
            validated_data['billing'] = billing
        elif billing_key:
            billing = create_portone_billing(user, billing_key)         
            validated_data['billing'] = billing
                
        # Point
        point_amount = validated_data.pop('point_amount', None)
        if point_amount:
            point_transaction = PointTransaction.objects.create(user=user, amount=-point_amount, transaction_type='SUBSCRIPTION')
            validated_data['point'] = point_transaction

        # Coupon
        coupon_id = validated_data.pop('coupon_id', None)
        user_coupon = None
        if coupon_id is not None:
            try:
                user_coupon = SubscriptionUserCoupon.objects.get(id=coupon_id, user=user, is_active=True, used_at__isnull=True)
                if not user_coupon.is_valid:
                    raise serializers.ValidationError("Invalid or expired coupon")
            except SubscriptionUserCoupon.DoesNotExist:
                raise serializers.ValidationError("Invalid or expired coupon")            
        validated_data['coupon'] = user_coupon

        # Payment
        payment_key = validated_data.pop('payment_key', None)
        order_id = validated_data.pop('order_id', None)
        month = validated_data.get('month')
        exchange_rate = validated_data.pop('exchange_rate', 1)

        subscription_request = SubscriptionRequest.objects.create(**validated_data)        

        if payment_key:
            car = subscription_request.car
            
            # Match month to subscription fee
            if month >= 96 and car.subscription_fee_96:
                base_amount_per_month = car.subscription_fee_96
            elif month >= 84 and car.subscription_fee_84:
                base_amount_per_month = car.subscription_fee_84
            elif month >= 72 and car.subscription_fee_72:
                base_amount_per_month = car.subscription_fee_72
            elif month >= 60 and car.subscription_fee_60:
                base_amount_per_month = car.subscription_fee_60
            elif month >= 48 and car.subscription_fee_48:
                base_amount_per_month = car.subscription_fee_48
            elif month >= 36 and car.subscription_fee_36:
                base_amount_per_month = car.subscription_fee_36
            elif month >= 24 and car.subscription_fee_24:
                base_amount_per_month = car.subscription_fee_24
            elif month >= 12 and car.subscription_fee_12:
                base_amount_per_month = car.subscription_fee_12
            elif month >= 6 and car.subscription_fee_6:
                base_amount_per_month = car.subscription_fee_6
            elif month >= 3 and car.subscription_fee_3:
                base_amount_per_month = car.subscription_fee_3
            elif month >= 1 and car.subscription_fee_1:
                base_amount_per_month = car.subscription_fee_1
            else:
                raise serializers.ValidationError(f"해당 차량({car.model.brand.name} {car.model.name})의 {month}개월 구독료 정보가 없습니다.")
            
            # Apply coupon discount first
            discounted_amount_per_month = base_amount_per_month
            if user_coupon:
                coupon = user_coupon.coupon
                if coupon.discount_type == 'PERCENTAGE':
                    discount = int(base_amount_per_month * (coupon.discount_rate / 100))
                    discount_amount = min(discount, coupon.max_discount)
                    discounted_amount_per_month -= discount_amount
                elif coupon.discount_type == 'FIXED':
                    discounted_amount_per_month -= coupon.discount
                elif coupon.discount_type == 'FREE':
                    discounted_amount_per_month = 0
            
            # Apply point discount to first month
            first_month_amount = max(0, discounted_amount_per_month - (point_amount if point_amount else 0))
            remaining_months = max(0, month - 1)
            amount = first_month_amount + (remaining_months * discounted_amount_per_month)
            payment = confirm_toss_payment(user, payment_key, int(amount)*int(exchange_rate), order_id)
            subscription_request.payment = payment

        # Subscription Request
        subscription_request.save()
        return subscription_request

    def update(self, instance, validated_data):
        # Point, Coupon not allowed to be updated
        validated_data.pop('point_amount', None)
        validated_data.pop('coupon_id', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Billing is allowed to be updated
        user = validated_data.get('user')
        auth_key = validated_data.pop('auth_key', None)
        customer_key = validated_data.pop('customer_key', None)
        billing_key = validated_data.pop('billing_key', None)
        if auth_key and customer_key:
            billing = create_toss_billing(user, auth_key, customer_key)
            if instance.billing:
                instance.billing.is_active = False
                instance.billing.save()
            validated_data['billing'] = billing
        elif billing_key:
            billing = create_portone_billing(user, billing_key)         
            if instance.billing:
                instance.billing.is_active = False
                instance.billing.save()
            validated_data['billing'] = billing

        # Subscription Request
        instance.save()
        return instance


class SubscriptionSerializer(serializers.ModelSerializer):
    request = SubscriptionRequestSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'request', 'start_date', 'end_date', 'is_active', 'is_current']
        read_only_fields = ['id', 'request', 'is_active', 'is_current']
    
    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("Start date must be before end date")
        
        return data
    

# Review Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class SubscriptionReviewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image']


class SubscriptionReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionReview
        fields = [
            'id', 'content', 'image', 'user', 'model',
            'created_at', 'modified_at', 'is_active', 'is_verified'
        ]
        read_only_fields = ['id', 'user', 'model', 'created_at', 'modified_at', 'is_active', 'is_verified']


class SubscriptionReviewDetailSerializer(SubscriptionReviewSerializer):
    user = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta(SubscriptionReviewSerializer.Meta):
        fields = SubscriptionReviewSerializer.Meta.fields + ['likes', 'is_liked']
        read_only_fields = SubscriptionReviewSerializer.Meta.read_only_fields + ['likes', 'is_liked']

    def get_user(self, obj):
        return SubscriptionReviewUserSerializer(obj.user).data

    def get_model(self, obj):
        return SubscriptionModelDetailSerializer(obj.model).data
    
    def get_likes(self, obj):
        return obj.subscription_review_likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscription_review_likes.filter(user=request.user).exists()
        return False


class SubscriptionReviewListSerializer(SubscriptionReviewDetailSerializer):
    content = serializers.SerializerMethodField()

    class Meta(SubscriptionReviewDetailSerializer.Meta):
        fields = SubscriptionReviewDetailSerializer.Meta.fields
        read_only_fields = SubscriptionReviewDetailSerializer.Meta.read_only_fields

    def get_content(self, obj):
        if obj.content:
            return obj.content[:40] + ("..." if len(obj.content) > 40 else "")
        return ""


# Model Request Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class SubscriptionModelRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModelRequest
        fields = ['id', 'user', 'model', 'created_at', 'modified_at', 'is_active']
        read_only_fields = ['id', 'user', 'created_at', 'modified_at', 'is_active']