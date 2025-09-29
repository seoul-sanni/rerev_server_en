# butlers/admin.py
app_name = 'butlers'

from django.contrib import admin

from .models import Butler, ButlerRequest, ButlerWayPoint, ButlerReview, ButlerLike, ButlerReviewLike, ButlerModelRequest, ButlerCoupon, ButlerUserCoupon

@admin.register(ButlerRequest)
class ButlerRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'car', 'start_at', 'start_location', 'end_at', 'end_location', 'created_at', 'modified_at', 'coupon', 'point', 'is_active']
    list_filter = ['created_at', 'modified_at', 'is_active']
    search_fields = ['user__username', 'user__email', 'car__model__name', 'car__model__brand__name', 'car__vin_number']
    readonly_fields = ['created_at', 'modified_at']
    autocomplete_fields = ['car']
    list_editable = ['is_active']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'car', 'start_at', 'start_location', 'end_at', 'end_location', 'description')
        }),
        ('Coupon Information', {
            'fields': ('coupon',)
        }),
        ('Point Information', {
            'fields': ('point',)
        }),
        ('Billing Information', {
            'fields': ('payment_id',)
        }),
        ('Status Information', {
            'fields': ('is_active',)
        }),
        ('System Information', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'car', 'car__model', 'car__model__brand', 'coupon', 'coupon__coupon', 'point'
        )


@admin.register(ButlerWayPoint)
class WayPointAdmin(admin.ModelAdmin):
    list_display = ['id', 'butler_request', 'address', 'scheduled_time', 'is_active', 'created_at', 'modified_at']
    list_filter = ['is_active', 'created_at', 'modified_at', 'scheduled_time']
    search_fields = ['address', 'butler_request__user__username', 'butler_request__user__email', 'butler_request__car__model__name', 'butler_request__car__model__brand__name']
    readonly_fields = ['created_at', 'modified_at']
    autocomplete_fields = ['butler_request']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('butler_request', 'address', 'scheduled_time')
        }),
        ('Status Information', {
            'fields': ('is_active',)
        }),
        ('System Information', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'butler_request', 'butler_request__user', 'butler_request__car', 'butler_request__car__model', 'butler_request__car__model__brand'
        )


@admin.register(Butler)
class ButlerAdmin(admin.ModelAdmin):
    list_display = ['id', 'request', 'created_at', 'modified_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'modified_at']
    search_fields = ['request__user__username', 'request__user__email', 'request__car__model__name', 'request__car__model__brand__name', 'request__car__vin_number']
    readonly_fields = ['created_at', 'modified_at']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('request',)
        }),
        ('Status Information', {
            'fields': ('is_active',)
        }),
        ('System Information', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'request', 'request__user', 'request__car', 'request__car__model', 'request__car__model__brand'
        )


@admin.register(ButlerLike)
class ButlerLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'model', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'model__name', 'model__brand__name']
    readonly_fields = ['created_at']
    autocomplete_fields = ['model']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'model')
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'model', 'model__brand'
        )


@admin.register(ButlerReview)
class ButlerReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'model', 'content_preview', 'is_verified', 'is_active', 'created_at']
    list_filter = ['is_verified', 'is_active', 'created_at', 'modified_at']
    search_fields = ['user__username', 'user__email', 'model__name', 'model__brand__name', 'content']
    readonly_fields = ['created_at', 'modified_at']
    autocomplete_fields = ['model']
    list_editable = ['is_verified', 'is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'model', 'content', 'image')
        }),
        ('Status Information', {
            'fields': ('is_verified', 'is_active')
        }),
        ('System Information', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'model', 'model__brand'
        )


@admin.register(ButlerReviewLike)
class ButlerReviewLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'review', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'review__content', 'review__model__name']
    readonly_fields = ['created_at']
    autocomplete_fields = ['review']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'review')
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'review', 'review__model', 'review__model__brand'
        )


@admin.register(ButlerModelRequest)
class ButlerModelRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'user__name', 'user__mobile', 'model', 'created_at', 'modified_at', 'is_active']
    list_filter = ['created_at', 'modified_at', 'is_active']
    search_fields = ['user__name', 'user__mobile', 'model']
    readonly_fields = ['created_at', 'modified_at']
    list_editable = ['is_active']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'model')
        }),
        ('Status Information', {
            'fields': ('is_active',)
        }),
        ('System Information', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ButlerCoupon)
class ButlerCouponAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'description', 'discount_type', 'discount_rate', 'max_discount', 'discount', 'valid_from', 'valid_to', 'is_active']
    list_filter = ['is_active', 'valid_from', 'valid_to', 'discount_type']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['code', 'created_at', 'modified_at']
    list_editable = ['is_active']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'discount_type', 'discount_rate', 'max_discount', 'discount')
        }),
        ('Application Scope', {
            'fields': ('brand_ids', 'model_ids', 'car_ids')
        }),
        ('Conditions', {
            'fields': ('min_price', 'max_price', 'usage_limit', 'usage_limit_per_user')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to', 'is_active')
        }),
        ('System Information', {
            'fields': ('code', 'created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ButlerUserCoupon)
class ButlerUserCouponAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'coupon', 'is_active', 'is_used', 'is_valid', 'created_at', 'used_at']
    list_filter = ['is_active', 'created_at', 'used_at', 'coupon__discount_type']
    search_fields = ['user__username', 'user__email', 'coupon__code', 'coupon__name']
    readonly_fields = ['created_at', 'modified_at']
    list_editable = ['is_active']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'coupon', 'is_active')
        }),
        ('Usage Information', {
            'fields': ('used_at',)
        }),
        ('System Information', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )

    def is_used(self, obj):
        return obj.used_at is not None
    is_used.boolean = True
    is_used.short_description = 'Used'

    def is_valid(self, obj):
        if not obj.is_active or obj.used_at is not None:
            return False
        return obj.coupon.is_valid_now
    is_valid.boolean = True
    is_valid.short_description = 'Valid'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'coupon')