# users/serializers.py
app_name = 'users'

from rest_framework import serializers

from .models import Referral, PointTransaction

class ReferralSerializer(serializers.ModelSerializer):
    referrer_username = serializers.SerializerMethodField()
    referree_username = serializers.SerializerMethodField()
    subscription_coupon_code = serializers.SerializerMethodField()
    
    class Meta:
        model = Referral
        fields = ['referrer', 'referrer_username', 'referree', 'referree_username', 'subscription_coupon', 'subscription_coupon_code', 'created_at', 'modified_at']
        read_only_fields = ['referrer', 'referrer_username', 'referree', 'referree_username', 'subscription_coupon', 'subscription_coupon_code', 'created_at', 'modified_at']
    
    def get_referrer_username(self, obj):
        return obj.referrer.username if obj.referrer else None
    
    def get_referree_username(self, obj):
        return obj.referree.username if obj.referree else None
    
    def get_subscription_coupon_code(self, obj):
        return obj.subscription_coupon.code if obj.subscription_coupon else None


class PointTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTransaction
        fields = ['id', 'user', 'amount', 'description', 'transaction_type', 'transaction_id', 'created_at', 'modified_at']
        read_only_fields = ['id', 'user', 'amount', 'description', 'transaction_type', 'transaction_id', 'created_at', 'modified_at']