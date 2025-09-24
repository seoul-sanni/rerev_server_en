# subscriptions/serializers.py
app_name = 'subscriptions'

from rest_framework import serializers

from django.utils import timezone

from cars.models import Brand, Model, Car
from users.models import PointTransaction
from accounts.models import User

from .models import Buttler, ButtlerRequest, ButtlerReview, ButtlerModelRequest, ButtlerCoupon, ButtlerUserCoupon

# Default Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class ButtlerBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'image']


class ButtlerModelSerializer(serializers.ModelSerializer):
    brand = ButtlerBrandSerializer(read_only=True)

    class Meta:
        model = Model
        fields = ['id', 'brand', 'name', 'image', 'code']


# Car Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class SimpleButtlerCarSerializer(serializers.ModelSerializer):
    model = ButtlerModelSerializer(read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'model', 'vin_number', 'license_plate', 'description', 'images', 'retail_price', 'release_date', 'mileage', 'is_new', 'is_hot',
        'is_subscriptable', 'subscription_fee_1', 'subscription_fee_3', 'subscription_fee_6', 'subscription_fee_12', 'subscription_fee_24',
        'subscription_fee_36', 'subscription_fee_48', 'subscription_fee_60', 'subscription_fee_72', 'subscription_fee_84', 'subscription_fee_96',
        ]


class ButtlerCarSerializer(serializers.ModelSerializer):
    buttler_info = serializers.SerializerMethodField()
    buttler_request_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Car
        fields = ['id', 'vin_number', 'license_plate', 'description', 'images', 'retail_price', 'release_date', 'mileage', 'is_new', 'is_hot',
        'is_subscriptable', 'subscription_fee_1', 'subscription_fee_3', 'subscription_fee_6', 'subscription_fee_12', 'subscription_fee_24',
        'subscription_fee_36', 'subscription_fee_48', 'subscription_fee_60', 'subscription_fee_72', 'subscription_fee_84', 'subscription_fee_96',
        'buttler_info', 'buttler_request_info'
        ]
    
    def get_buttler_info(self, obj):
        now = timezone.now().date()  # datetime.date로 변환
        buttler_list = []
        
        for buttler_request in obj.buttler_requests.filter(end_at__gte=now, is_active=False):
            buttler_list.append({
                'buttler_start': buttler_request.start_at,
                'buttler_end': buttler_request.end_at,
            })
        
        if buttler_list:
            return buttler_list

        return None

    def get_buttler_request_info(self, obj):
        now = timezone.now().date()  # datetime.date로 변환
        buttler_request_list = []
        
        for buttler_request in obj.buttler_requests.filter(end_at__gte=now, is_active=True):
            buttler_request_list.append({
                'buttler_start': buttler_request.start_at,
                'buttler_end': buttler_request.end_at,
            })

        if buttler_request_list:
            return buttler_request_list
        
        return None


class ButtlerCarDetailSerializer(ButtlerCarSerializer):
    model = ButtlerModelSerializer(read_only=True)
    
    class Meta:
        model = Car
        fields = ButtlerCarSerializer.Meta.fields + ['model']


# Model Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class ButtlerModelListSerializer(serializers.ModelSerializer):
    brand = ButtlerBrandSerializer(read_only=True)
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
        return ButtlerCarSerializer


class ButtlerModelDetailSerializer(ButtlerModelListSerializer):
    def get_car_serializer(self):
        return ButtlerCarSerializer


# Coupon Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class ButtlerCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = ButtlerCoupon
        fields = ['id', 'code', 'name', 'description', 'brand_ids', 'model_ids', 'car_ids', 'discount_type', 'discount_rate', 'max_discount', 'discount', 'min_price', 'max_price', 'valid_from', 'valid_to', 'is_specific']
        read_only_fields = ['id', 'code', 'created_at', 'modified_at']


class ButtlerUserCouponSerializer(serializers.ModelSerializer):
    coupon = ButtlerCouponSerializer(read_only=True)

    class Meta:
        model = ButtlerUserCoupon
        fields = ['id', 'user', 'coupon', 'is_active', 'is_used', 'is_valid', 'created_at', 'used_at']
        read_only_fields = ['id', 'user', 'coupon', 'is_used', 'is_valid', 'created_at', 'modified_at', 'used_at']


# Subscription Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class ButtlerRequestSerializer(serializers.ModelSerializer):
    car = SimpleButtlerCarSerializer(read_only=True)
    coupon_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    coupon = ButtlerUserCouponSerializer(read_only=True)
    point_amount = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    point_used = serializers.SerializerMethodField(read_only=True)
    payment_id = serializers.CharField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = ButtlerRequest
        fields = ['id', 'user', 'car', 'start_at', 'end_at', 'point_used', 'created_at', 'modified_at', 'coupon_id', 'coupon', 'is_active', 'point_amount', 'payment_id']
        read_only_fields = ['id', 'user', 'car', 'point_used', 'end_at', 'created_at', 'modified_at', 'coupon', 'is_active']
    
    def get_point_used(self, obj):
        if obj.point:
            return -obj.point.amount
        return None
    
    def create(self, validated_data):
        point_amount = validated_data.pop('point_amount', None)
        if point_amount:
            point_transaction = PointTransaction.objects.create(user=validated_data.get('user'), amount=-point_amount, transaction_type='BUTTLER')
            validated_data['point'] = point_transaction

        coupon_id = validated_data.pop('coupon_id', None)
        user_coupon = None
        if coupon_id is not None:
            try:
                user = validated_data.get('user')
                user_coupon = ButtlerUserCoupon.objects.get(id=coupon_id, user=user, is_active=True, used_at__isnull=True)
                
                if not user_coupon.is_valid:
                    raise serializers.ValidationError("Invalid or expired coupon")

            except ButtlerUserCoupon.DoesNotExist:
                raise serializers.ValidationError("Invalid or expired coupon")
        
        buttler_request = ButtlerRequest.objects.create(**validated_data, coupon=user_coupon)        
        return buttler_request


class ButtlerSerializer(serializers.ModelSerializer):
    request = ButtlerRequestSerializer(read_only=True)

    class Meta:
        model = Buttler
        fields = ['id', 'request', 'created_at', 'modified_at', 'is_active']
        read_only_fields = ['id', 'request', 'created_at', 'modified_at', 'is_active']


# Review Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class ButtlerReviewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image']


class ButtlerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ButtlerReview
        fields = [
            'id', 'content', 'image', 'user', 'model',
            'created_at', 'modified_at', 'is_active', 'is_verified'
        ]
        read_only_fields = ['id', 'user', 'model', 'created_at', 'modified_at', 'is_active', 'is_verified']


class ButtlerReviewDetailSerializer(ButtlerReviewSerializer):
    user = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta(ButtlerReviewSerializer.Meta):
        fields = ButtlerReviewSerializer.Meta.fields + ['likes', 'is_liked']
        read_only_fields = ButtlerReviewSerializer.Meta.read_only_fields + ['likes', 'is_liked']

    def get_user(self, obj):
        return ButtlerReviewUserSerializer(obj.user).data

    def get_model(self, obj):
        return ButtlerModelDetailSerializer(obj.model).data
    
    def get_likes(self, obj):
        return obj.buttler_review_likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.buttler_review_likes.filter(user=request.user).exists()
        return False


class ButtlerReviewListSerializer(ButtlerReviewDetailSerializer):
    content = serializers.SerializerMethodField()

    class Meta(ButtlerReviewDetailSerializer.Meta):
        fields = ButtlerReviewDetailSerializer.Meta.fields
        read_only_fields = ButtlerReviewDetailSerializer.Meta.read_only_fields

    def get_content(self, obj):
        if obj.content:
            return obj.content[:40] + ("..." if len(obj.content) > 40 else "")
        return ""


# Model Request Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class ButtlerModelRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ButtlerModelRequest
        fields = ['id', 'user', 'model', 'created_at', 'modified_at', 'is_active']
        read_only_fields = ['id', 'user', 'created_at', 'modified_at', 'is_active']