# cars/admin.py
app_name = 'cars'

from django.contrib import admin
from .models import Brand, Model, Car

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at', 'modified_at']
    list_filter = ['created_at', 'modified_at']
    search_fields = ['name', 'slug', 'description']
    readonly_fields = ['created_at', 'modified_at']
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('System Information', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'slug', 'brand', 'created_at']
    list_filter = ['brand', 'created_at', 'modified_at']
    search_fields = ['name', 'code', 'slug', 'description', 'brand__name']
    readonly_fields = ['slug', 'created_at', 'modified_at']
    autocomplete_fields = ['brand']
    fieldsets = (
        ('Basic Information', {
            'fields': ('brand', 'name', 'code', 'slug', 'description', 'image', 'front_image', 'rear_image')
        }),
        ('System Information', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['id', 'model', 'sub_model', 'license_plate', 'is_sellable', 'is_subscriptable', 'is_butler', 'is_new', 'is_hot', 'is_active']
    list_filter = ['is_sellable', 'is_subscriptable', 'is_new', 'is_hot', 'is_active', 'release_date', 'created_at', 'modified_at']
    search_fields = ['vin_number', 'license_plate', 'model__name', 'model__brand__name', 'description']
    readonly_fields = ['subscription_fee_minimum', 'subscription_available_from', 'butler_reservated_dates', 'butler_available_from', 'created_at', 'modified_at']
    autocomplete_fields = ['model']
    list_editable = ['is_sellable', 'is_subscriptable', 'is_butler', 'is_new', 'is_hot', 'is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('model', 'sub_model', 'trim', 'color', 'vin_number', 'license_plate', 'description', 'images', 'inspection_report')
        }),
        ('Vehicle Information', {
            'fields': ('retail_price', 'release_date', 'mileage')
        }),
        ('Sell Information', {
            'fields': ('is_sellable', 'sell_price')
        }),
        ('Subscription Information', {
            'fields': ('is_subscriptable', 'subscription_fee_1', 'subscription_fee_3', 'subscription_fee_6', 'subscription_fee_12', 'subscription_fee_24',
            'subscription_fee_36', 'subscription_fee_48', 'subscription_fee_60', 'subscription_fee_72', 'subscription_fee_84', 'subscription_fee_96',
            'subscription_fee_minimum', 'subscription_available_from'
            )
        }),
        ('Butler Information', {
            'fields': ('is_butler', 'butler_fee', 'butler_overtime_fee', 'butler_reservated_dates', 'butler_available_from')
        }),
        ('System Information', {
            'fields': ('is_new', 'is_hot', 'is_active', 'created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )