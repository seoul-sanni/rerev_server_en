# butlers/serializers.py
app_name = 'butlers'

from datetime import timedelta

from rest_framework import serializers

from cars.models import Brand, Model, Car
from users.models import PointTransaction
from accounts.models import User

from .models import Butler, ButlerRequest, ButlerWayPoint, ButlerReview, ButlerModelRequest, ButlerCoupon, ButlerUserCoupon

# Default Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class ButlerBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'image']


class SimpleButlerModelSerializer(serializers.ModelSerializer):
    car_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Model
        fields = ['id', 'name', 'image', 'front_image', 'rear_image', 'code', 'slug', 'car_count']
    
    def get_car_count(self, obj):
        return obj.cars.filter(is_active=True, is_butler=True).count()


class ButlerModelSerializer(serializers.ModelSerializer):
    brand = ButlerBrandSerializer(read_only=True)

    class Meta:
        model = Model
        fields = ['id', 'brand', 'name', 'code', 'image', 'front_image', 'rear_image', 'slug']


# Car Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class SimpleButlerCarSerializer(serializers.ModelSerializer):
    model = ButlerModelSerializer(read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'model', 'sub_model', 'trim', 'color', 'license_plate', 'description', 'images', 'retail_price', 'release_date', 'mileage', 'is_new', 'is_hot',
        'is_butler', 'butler_fee', 'butler_overtime_fee', 'butler_reservated_dates', 'butler_available_from'
        ]


class ButlerCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'sub_model', 'trim', 'color', 'license_plate', 'description', 'images', 'retail_price', 'release_date', 'mileage', 'is_new', 'is_hot',
        'is_butler', 'butler_fee', 'butler_overtime_fee', 'butler_reservated_dates', 'butler_available_from'
        ]


class ButlerCarDetailSerializer(ButlerCarSerializer):
    model = ButlerModelSerializer(read_only=True)
    
    class Meta:
        model = Car
        fields = ButlerCarSerializer.Meta.fields + ['model']


# Model Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class ButlerModelListSerializer(serializers.ModelSerializer):
    brand = ButlerBrandSerializer(read_only=True)
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
        return ButlerCarSerializer


class ButlerModelDetailSerializer(ButlerModelListSerializer):
    def get_car_serializer(self):
        return ButlerCarSerializer


# Coupon Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class ButlerCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = ButlerCoupon
        fields = ['id', 'code', 'name', 'description', 'brand_ids', 'model_ids', 'car_ids', 'discount_type', 'discount_rate', 'max_discount', 'discount', 'min_price', 'max_price', 'valid_from', 'valid_to', 'is_specific']
        read_only_fields = ['id', 'code', 'created_at', 'modified_at']


class ButlerUserCouponSerializer(serializers.ModelSerializer):
    coupon = ButlerCouponSerializer(read_only=True)

    class Meta:
        model = ButlerUserCoupon
        fields = ['id', 'user', 'coupon', 'is_active', 'is_used', 'is_valid', 'created_at', 'used_at']
        read_only_fields = ['id', 'user', 'coupon', 'is_used', 'is_valid', 'created_at', 'modified_at', 'used_at']


# Butler Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class ButlerWayPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ButlerWayPoint
        fields = ['id', 'address', 'scheduled_time']


class ButlerRequestSerializer(serializers.ModelSerializer):
    car = SimpleButlerCarSerializer(read_only=True)
    coupon_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    coupon = ButlerUserCouponSerializer(read_only=True)
    point_amount = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    point_used = serializers.SerializerMethodField(read_only=True)
    payment_id = serializers.CharField(write_only=True, required=False, allow_null=True)
    way_point_requests = ButlerWayPointSerializer(write_only=True, required=False, allow_null=True, many=True)
    way_points = ButlerWayPointSerializer(source='butler_way_points', read_only=True, many=True)
    
    class Meta:
        model = ButlerRequest
        fields = ['id', 'user', 'car', 'start_at', 'start_location', 'end_at', 'end_location', 'description', 'point_used', 'created_at', 'modified_at', 'coupon_id', 'coupon', 'is_active', 'point_amount', 'payment_id', 'way_point_requests', 'way_points']
        read_only_fields = ['id', 'user', 'car', 'point_used', 'created_at', 'modified_at', 'coupon', 'is_active', 'way_points']
    
    def get_point_used(self, obj):
        if obj.point:
            return -obj.point.amount
        return None
    
    def create(self, validated_data):
        point_amount = validated_data.pop('point_amount', None)
        if point_amount:
            point_transaction = PointTransaction.objects.create(user=validated_data.get('user'), amount=-point_amount, transaction_type='BUTLER')
            validated_data['point'] = point_transaction

        coupon_id = validated_data.pop('coupon_id', None)
        user_coupon = None
        if coupon_id is not None:
            try:
                user = validated_data.get('user')
                user_coupon = ButlerUserCoupon.objects.get(id=coupon_id, user=user, is_active=True, used_at__isnull=True)
                
                if not user_coupon.is_valid:
                    raise serializers.ValidationError("Invalid or expired coupon")

            except ButlerUserCoupon.DoesNotExist:
                raise serializers.ValidationError("Invalid or expired coupon")
        
        way_point_requests = validated_data.pop('way_point_requests', [])        
        butler_request = ButlerRequest.objects.create(**validated_data, coupon=user_coupon)

        for way_point_request in way_point_requests:
            ButlerWayPoint.objects.create(butler_request=butler_request, address=way_point_request['address'], scheduled_time=way_point_request['scheduled_time'])
        
        return butler_request

    def update(self, instance, validated_data):
        validated_data.pop('point_amount', None)
        validated_data.pop('coupon_id', None)
        validated_data.pop('way_point_requests', None)
        
        if 'start_at' in validated_data and 'end_at' not in validated_data:
            validated_data['end_at'] = validated_data['start_at'] + timedelta(hours=10)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class ButlerSerializer(serializers.ModelSerializer):
    request = ButlerRequestSerializer(read_only=True)

    class Meta:
        model = Butler
        fields = ['id', 'request', 'created_at', 'modified_at', 'is_active']
        read_only_fields = ['id', 'request', 'created_at', 'modified_at', 'is_active']


# Review Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class ButlerReviewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image']


class ButlerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ButlerReview
        fields = [
            'id', 'content', 'image', 'user', 'model',
            'created_at', 'modified_at', 'is_active', 'is_verified'
        ]
        read_only_fields = ['id', 'user', 'model', 'created_at', 'modified_at', 'is_active', 'is_verified']


class ButlerReviewDetailSerializer(ButlerReviewSerializer):
    user = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta(ButlerReviewSerializer.Meta):
        fields = ButlerReviewSerializer.Meta.fields + ['likes', 'is_liked']
        read_only_fields = ButlerReviewSerializer.Meta.read_only_fields + ['likes', 'is_liked']

    def get_user(self, obj):
        return ButlerReviewUserSerializer(obj.user).data

    def get_model(self, obj):
        return ButlerModelDetailSerializer(obj.model).data
    
    def get_likes(self, obj):
        return obj.butler_review_likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.butler_review_likes.filter(user=request.user).exists()
        return False


class ButlerReviewListSerializer(ButlerReviewDetailSerializer):
    content = serializers.SerializerMethodField()

    class Meta(ButlerReviewDetailSerializer.Meta):
        fields = ButlerReviewDetailSerializer.Meta.fields
        read_only_fields = ButlerReviewDetailSerializer.Meta.read_only_fields

    def get_content(self, obj):
        if obj.content:
            return obj.content[:40] + ("..." if len(obj.content) > 40 else "")
        return ""


# Model Request Serializer
# <-------------------------------------------------------------------------------------------------------------------------------->
class ButlerModelRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ButlerModelRequest
        fields = ['id', 'user', 'model', 'created_at', 'modified_at', 'is_active']
        read_only_fields = ['id', 'user', 'created_at', 'modified_at', 'is_active']