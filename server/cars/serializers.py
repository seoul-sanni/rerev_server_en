# cars/serializers.py
app_name = 'cars'

from rest_framework import serializers
from .models import Brand, Model, Car

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'image', 'description']


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ['id', 'name', 'image', 'description']


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = [
            'id', 'model', 'sub_model', 'trim', 'color', 'vin_number', 'license_plate', 'description', 'images', 'inspection_report', 'retail_price', 'release_date', 'mileage', 
            'is_sellable', 'sell_price',
            'is_subscriptable',
            'subscription_fee_1', 'subscription_fee_3', 'subscription_fee_6', 'subscription_fee_12', 'subscription_fee_24',
            'subscription_fee_36', 'subscription_fee_48', 'subscription_fee_60', 'subscription_fee_72', 'subscription_fee_84', 'subscription_fee_96',
            'is_buttler', 'buttler_price',
            'created_at', 'modified_at', 'is_new', 'is_hot', 'is_active'
        ]