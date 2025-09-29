# subscriptions/urls.py
app_name = 'subscriptions'

from django.urls import path

from .views import GarageAPIView
from .views import ModelListAPIView, ModelDetailAPIView
from .views import CarListAPIView, CarDetailAPIView
from .views import SubscriptionAPIView, SubscriptionRequestListAPIView, SubscriptionRequestAPIView, SubscriptionRequestDetailAPIView
from .views import LikeAPIView, ReviewListAPIView, ReviewAPIView, ReviewDetailAPIView, ReviewLikeAPIView
from .views import ModelRequestAPIView
from .views import CouponListAPIView, CouponDetailAPIView

urlpatterns = [
    path('', SubscriptionAPIView.as_view(), name='subscription'),
    path('/requests', SubscriptionRequestListAPIView.as_view(), name='subscription-request'),
    path('/requests/<int:request_id>', SubscriptionRequestDetailAPIView.as_view(), name='subscription-request-detail'),

    path('/garages', GarageAPIView.as_view(), name='garage-list'),

    path('/models/request', ModelRequestAPIView.as_view(), name='model-request'),                   # 모델 요청
    path('/models', ModelListAPIView.as_view(), name='model-list'),                                 # 모델 목록
    path('/models/<int:model_id>', ModelDetailAPIView.as_view(), name='model-detail'),              # 모델 상세
    path('/models/<int:model_id>/likes', LikeAPIView.as_view(), name='like-model'),                 # 모델 좋아요
    path('/models/<int:model_id>/reviews', ReviewAPIView.as_view(), name='review-list'),            # 리뷰 목록

    path('/cars', CarListAPIView.as_view(), name='car-list'),                                       # 자동차 목록
    path('/cars/<int:car_id>', CarDetailAPIView.as_view(), name='car-detail'),                      # 자동차 상세
    path('/cars/<int:car_id>/request', SubscriptionRequestAPIView.as_view(), name='add-subscription-request'),# 구독 요청

    path('/reviews', ReviewListAPIView.as_view(), name='review-list'),                              # 리뷰 목록
    path('/reviews/<int:review_id>', ReviewDetailAPIView.as_view(), name='review-detail'),          # 리뷰 상세
    path('/reviews/<int:review_id>/likes', ReviewLikeAPIView.as_view(), name='review-like'),        # 리뷰 좋아요

    path('/coupons', CouponListAPIView.as_view(), name='coupon-list'),                              # 쿠폰 목록
    path('/coupons/<str:coupon_code>', CouponDetailAPIView.as_view(), name='coupon-detail'),        # 쿠폰 상세
]