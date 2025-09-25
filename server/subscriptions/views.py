# subscriptions/views.py
app_name = 'subscriptions'

from collections import defaultdict

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.utils import timezone
from django.db.models import Prefetch, Q

from drf_spectacular.utils import extend_schema

from server.utils import SuccessResponseBuilder, ErrorResponseBuilder
from cars.models import Brand, Model, Car

from .task import send_subscription_email
from .models import Subscription, SubscriptionRequest, SubscriptionLike, SubscriptionReview, SubscriptionReviewLike, SubscriptionCoupon, SubscriptionUserCoupon
from .serializers import SimpleSubscriptionModelSerializer, SubscriptionModelListSerializer, SubscriptionModelDetailSerializer, SubscriptionCarDetailSerializer
from .serializers import SubscriptionSerializer, SubscriptionRequestSerializer
from .serializers import SubscriptionReviewSerializer, SubscriptionReviewDetailSerializer, SubscriptionModelRequestSerializer
from .serializers import SubscriptionCouponSerializer, SubscriptionUserCouponSerializer
from .permissions import AllowAny, IsAuthenticated, IsCIVerified, IsAuthor, IsSubscripted
from .paginations import SubscriptionPagination
from .schemas import GarageSchema, CouponSchema, SubscriptionSchema, ReviewSchema

# Garage APIs
# <-------------------------------------------------------------------------------------------------------------------------------->
# Garage 목록을 조회하는 API
class GarageAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class = SubscriptionPagination

    @extend_schema(**GarageSchema.get_garage())
    def get(self, request):
        brand_model_dict = defaultdict(list)
        for model in Model.objects.select_related('brand').all():
            brand_model_dict[model.brand].append(model)
        
        garage_list = []
        for brand, models in brand_model_dict.items():
            garage_item = {
                'name': brand.name,
                'slug': brand.slug,
                'model_list': SimpleSubscriptionModelSerializer(models, many=True).data
            }
            garage_list.append(garage_item)

        brands = request.query_params.getlist('brand')
        models = request.query_params.getlist('model')
        months = request.query_params.getlist('month')
        available_only = request.query_params.get('available_only')
        sort = request.query_params.get('sort')
        order = request.query_params.get('order')

        try:
            cars_queryset = Car.objects.filter(is_active=True, is_subscriptable=True).select_related('model', 'model__brand')

            # (brand OR model) AND (month_option_1 OR month_option_2 ...)
            if brands or models:
                filter_conditions = Q()
                if brands:
                    filter_conditions |= Q(model__brand__slug__in=brands)
                if models:
                    filter_conditions |= Q(model__slug__in=models)
                cars_queryset = cars_queryset.filter(filter_conditions)
            
            if months:
                month_filters = []
                for month in months:
                    if month == '1':
                        month_filters.append(Q(subscription_fee_1__isnull=False))
                    elif month == '3':
                        month_filters.append(Q(subscription_fee_3__isnull=False))
                    elif month == '6':
                        month_filters.append(Q(subscription_fee_6__isnull=False))
                    elif month == '12':
                        month_filters.append(Q(subscription_fee_12__isnull=False))
                    elif month == '24':
                        month_filters.append(Q(subscription_fee_24__isnull=False))
                    elif month == '36':
                        month_filters.append(Q(subscription_fee_36__isnull=False))
                    elif month == '48':
                        month_filters.append(Q(subscription_fee_48__isnull=False))
                    elif month == '60':
                        month_filters.append(Q(subscription_fee_60__isnull=False))
                    elif month == '72':
                        month_filters.append(Q(subscription_fee_72__isnull=False))
                    elif month == '84':
                        month_filters.append(Q(subscription_fee_84__isnull=False))
                    elif month == '96':
                        month_filters.append(Q(subscription_fee_96__isnull=False))
                
                if month_filters:
                    combined_filter = Q()
                    for filter_condition in month_filters:
                        combined_filter |= filter_condition
                    cars_queryset = cars_queryset.filter(combined_filter)
            
            if available_only:
                today = timezone.now().date()
                cars_queryset = cars_queryset.filter(
                    Q(subscription_available_from__isnull=True) |
                    Q(subscription_available_from__lte=today)
                )
            
            if sort:
                valid_sort_fields = ['subscription_available_from', 'subscription_fee_minimum', 'mileage', 'release_date']
                if sort in valid_sort_fields:
                    if order == 'desc':
                        sort_field = f'-{sort}'
                    else:
                        sort_field = sort
                    cars_queryset = cars_queryset.order_by(sort_field)
            
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(cars_queryset, request)
            if page is not None:
                pagination_info = {
                    'count': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'page_size': paginator.page_size,
                    'current_page': paginator.page.number,
                    'total_pages': paginator.page.paginator.num_pages
                }

                response_data = {
                    'garage_list': garage_list,
                    'cars': SubscriptionCarDetailSerializer(page, many=True).data,
                    'pagination_info': pagination_info
                }
                response = SuccessResponseBuilder().with_message("차고 목록 조회 성공").with_data(response_data).build()
                return Response(response, status=status.HTTP_200_OK)
                
            else:
                response_data = {
                    'garage_list': garage_list,
                    'cars': SubscriptionCarDetailSerializer(cars_queryset, many=True).data,
                }    
                response = SuccessResponseBuilder().with_message("차고 목록 조회 성공").with_data(response_data).build()
                return Response(response, status=status.HTTP_200_OK)
                
        except Exception as e:
            response = ErrorResponseBuilder().with_message("차고 목록을 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 구독 가능한 자동차 모델 목록을 조회하는 API
class ModelListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(**GarageSchema.get_model_list())
    def get(self, request):
        try:
            models = Model.objects.filter(
                cars__is_active=True,
                cars__is_subscriptable=True
            ).select_related('brand').prefetch_related(
                Prefetch(
                    'cars',
                    queryset=Car.objects.filter(
                        is_active=True,
                        is_subscriptable=True
                    ).prefetch_related('subscription_requests', 'subscription_requests__subscriptions')
                )
            ).distinct().order_by('brand__name', 'name')
            
            serializer = SubscriptionModelListSerializer(models, many=True)
            response = SuccessResponseBuilder().with_message("모델 목록 조회 성공").with_data({'models': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("모델 목록을 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 특정 자동차 모델의 상세 정보를 조회하는 API
class ModelDetailAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(**GarageSchema.get_model_detail())
    def get(self, request, model_id):
        try:
            model = Model.objects.filter(
                id=model_id,
                cars__is_active=True,
                cars__is_subscriptable=True
            ).select_related('brand').prefetch_related(
                'cars', 'cars__subscription_requests', 'cars__subscription_requests__subscriptions'
            ).first()
            
            if not model:
                response = ErrorResponseBuilder().with_message("요청하신 모델을 찾을 수 없거나 구독이 불가능합니다.").build()
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            
            serializer = SubscriptionModelDetailSerializer(model)
            response = SuccessResponseBuilder().with_message("모델 상세 정보 조회 성공").with_data({'model': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)
            
        except Exception as e:
            response = ErrorResponseBuilder().with_message("모델 상세 정보를 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 구독 가능한 자동차 목록을 조회하는 API
class CarListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(**GarageSchema.get_car_list())
    def get(self, request):
        try:            
            # 성능 최적화: 3개 간단한 쿼리로 분리 (더 빠름)
            base_queryset = Car.objects.filter(is_active=True, is_subscriptable=True).select_related('model', 'model__brand')
            
            # 1. upcoming_cars: 구독 가능일이 오늘 이후인 차량 10개 (가장 빠른 날짜순)
            today = timezone.now().date()
            upcoming_cars = list(base_queryset.filter(
                subscription_available_from__isnull=False,
                subscription_available_from__gt=today
            ).order_by('subscription_available_from')[:10])
            used_ids = {car.id for car in upcoming_cars}
            
            # 2. new_cars: 최신 차량 10개 (upcoming_cars 제외)
            new_cars = list(base_queryset.filter(is_new=True).exclude(id__in=used_ids).order_by('-created_at')[:10])
            used_ids.update(car.id for car in new_cars)
            
            # 3. hot_cars: 인기 차량 10개 (위 두 카테고리 제외)
            hot_cars = list(base_queryset.filter(is_hot=True).exclude(id__in=used_ids).order_by('-created_at')[:10])
            
            # 각각 시리얼라이징
            new_cars_data = SubscriptionCarDetailSerializer(new_cars, many=True).data
            hot_cars_data = SubscriptionCarDetailSerializer(hot_cars, many=True).data
            upcoming_cars_data = SubscriptionCarDetailSerializer(upcoming_cars, many=True).data
            
            response_data = {
                'new_cars': new_cars_data,
                'hot_cars': hot_cars_data,
                'upcoming_cars': upcoming_cars_data
            }
            
            response = SuccessResponseBuilder().with_message("차량 목록 조회 성공").with_data(response_data).build()
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("차량 목록을 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 특정 자동차의 상세 정보를 조회하는 API
class CarDetailAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(**GarageSchema.get_car_detail())
    def get(self, request, car_id):
        try:
            car = Car.objects.filter(
                id=car_id,
                is_active=True,
                is_subscriptable=True
            ).select_related('model', 'model__brand').first()
            
            if not car:
                response = ErrorResponseBuilder().with_message("요청하신 차량을 찾을 수 없거나 구독이 불가능합니다.").build()
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            
            serializer = SubscriptionCarDetailSerializer(car)
            response = SuccessResponseBuilder().with_message("차량 상세 정보 조회 성공").with_data({'car': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)
            
        except Exception as e:
            response = ErrorResponseBuilder().with_message("차량 상세 정보를 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Coupon APIs
# <-------------------------------------------------------------------------------------------------------------------------------->
# Coupon 목록을 조회하는 API
class CouponListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**CouponSchema.get_coupon_list())
    def get(self, request):
        try:
            user_coupons = SubscriptionUserCoupon.objects.filter(user=request.user)
            serializer = SubscriptionUserCouponSerializer(user_coupons, many=True)
            response = SuccessResponseBuilder().with_message("쿠폰 목록 조회 성공").with_data({'coupons': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("쿠폰 목록을 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CouponDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**CouponSchema.get_coupon_detail())
    def get(self, request, coupon_code):
        try:
            coupon = SubscriptionCoupon.objects.get(code=coupon_code)
            serializer = SubscriptionCouponSerializer(coupon)
            response = SuccessResponseBuilder().with_message("쿠폰 상세 정보 조회 성공").with_data({'coupon': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("쿠폰 정보를 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @extend_schema(**CouponSchema.add_coupon())
    def post(self, request, coupon_code):
        try:
            coupon = SubscriptionCoupon.objects.get(code=coupon_code)
            serializer = SubscriptionUserCouponSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, coupon=coupon)
                response = SuccessResponseBuilder().with_message("쿠폰 추가 성공").with_data({'coupon': serializer.data}).build()
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = ErrorResponseBuilder().with_message("입력 정보가 올바르지 않습니다.").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("쿠폰을 추가하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 구독 APIs
# <-------------------------------------------------------------------------------------------------------------------------------->
# 구독 요청 정보를 조회하는 API
class SubscriptionRequestListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**SubscriptionSchema.get_subscription_request_list())
    def get(self, request):
        try:
            subscription_requests = SubscriptionRequest.objects.filter(user=request.user, is_active=True).select_related('car', 'car__model', 'car__model__brand')
            serializer = SubscriptionRequestSerializer(subscription_requests, many=True)
            response = SuccessResponseBuilder().with_message("구독 요청 목록 조회 성공").with_data({'subscription_requests': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("구독 요청 목록을 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 구독 요청 API
class SubscriptionRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**SubscriptionSchema.create_subscription_request())
    def post(self, request, car_id):
        try:
            serializer = SubscriptionRequestSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, car_id=car_id)
                send_subscription_email.delay("seobioh@gmail.com", serializer.data)
                response = SuccessResponseBuilder().with_message("구독 요청 추가 성공").with_data({'subscription_request': serializer.data}).build()
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = ErrorResponseBuilder().with_message("입력 정보가 올바르지 않습니다.").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Car.DoesNotExist:
            response = ErrorResponseBuilder().with_message("요청하신 차량을 찾을 수 없습니다.").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("구독 요청을 추가하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 구독 정보를 조회하는 API
class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**SubscriptionSchema.get_subscription_list())
    def get(self, request):
        try:
            subscriptions = Subscription.objects.filter(request__user=request.user).select_related('request', 'request__user', 'request__car', 'request__car__model', 'request__car__model__brand')
            serializer = SubscriptionSerializer(subscriptions, many=True)
            response = SuccessResponseBuilder().with_message("구독 목록 조회 성공").with_data({'subscriptions': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("구독 목록을 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 좋아요 APIs
# <-------------------------------------------------------------------------------------------------------------------------------->
# 좋아요 추가 API
class LikeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    # 모델 좋아요 여부 조회
    @extend_schema(**GarageSchema.get_model_like_status())
    def get(self, request, model_id):
        try:
            model = Model.objects.get(id=model_id)
            liked = SubscriptionLike.objects.filter(user=request.user, model=model).exists()
            response = SuccessResponseBuilder().with_message("모델 좋아요 여부 조회 성공").with_data({'liked': liked}).build()
            return Response(response, status=status.HTTP_200_OK)

        except Model.DoesNotExist:
            response = ErrorResponseBuilder().with_message("요청하신 모델을 찾을 수 없습니다.").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("좋아요 상태를 확인하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 모델 좋아요 추가
    @extend_schema(**GarageSchema.add_model_like())
    def post(self, request, model_id):
        try:
            model = Model.objects.get(id=model_id)
            SubscriptionLike.objects.get_or_create(user=request.user, model=model)
            response = SuccessResponseBuilder().with_message("모델 좋아요 추가 성공").with_data({'message': 'Liked'}).build()
            return Response(response, status=status.HTTP_200_OK)
                
        except Model.DoesNotExist:
            response = ErrorResponseBuilder().with_message("요청하신 모델을 찾을 수 없습니다.").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("좋아요를 추가하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 모델 좋아요 취소
    @extend_schema(**GarageSchema.remove_model_like())
    def delete(self, request, model_id):
        try:
            model = Model.objects.get(id=model_id)
            SubscriptionLike.objects.filter(user=request.user, model=model).delete()
            response = SuccessResponseBuilder().with_message("모델 좋아요 취소 성공").with_data({'message': 'UnLiked'}).build()
            return Response(response, status=status.HTTP_200_OK)
                
        except Model.DoesNotExist:
            response = ErrorResponseBuilder().with_message("요청하신 모델을 찾을 수 없습니다.").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("좋아요를 취소하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 리뷰 APIs
# <-------------------------------------------------------------------------------------------------------------------------------->
# 모든 리뷰 목록을 조회하는 API
class ReviewListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(**ReviewSchema.get_review_list())
    def get(self, request):
        try:
            reviews = SubscriptionReview.objects.all()
            serializer = SubscriptionReviewSerializer(reviews, many=True)
            response = SuccessResponseBuilder().with_message("리뷰 목록 조회 성공").with_data({'reviews': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("리뷰 목록을 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 리뷰 추가 API
class ReviewAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        else :
            return [IsSubscripted()]

    @extend_schema(**ReviewSchema.get_review_list())
    def get(self, request, model_id):
        try:
            reviews = SubscriptionReview.objects.filter(model_id=model_id)
            serializer = SubscriptionReviewSerializer(reviews, many=True)
            response = SuccessResponseBuilder().with_message("리뷰 목록 조회 성공").with_data({'reviews': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("리뷰 목록을 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(**ReviewSchema.create_review())
    def post(self, request, model_id):
        try:
            model = Model.objects.get(id=model_id)
            self.check_object_permissions(request, model)
            serializer = SubscriptionReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, model_id=model_id)
                response = SuccessResponseBuilder().with_message("리뷰 추가 성공").with_data({'review': serializer.data}).build()
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = ErrorResponseBuilder().with_message("입력 정보가 올바르지 않습니다.").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("리뷰를 추가하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 리뷰 조회 API
class ReviewDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        else :
            return [IsAuthor()]

    # 리뷰 상세 조회
    @extend_schema(**ReviewSchema.get_review_detail())
    def get(self, request, review_id):
        try:
            review = SubscriptionReview.objects.get(id=review_id)
            self.check_object_permissions(request, review)
            serializer = SubscriptionReviewDetailSerializer(review, context={'request': request})
            response = SuccessResponseBuilder().with_message("리뷰 상세 조회 성공").with_data({'review': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)
        except SubscriptionReview.DoesNotExist:
            response = ErrorResponseBuilder().with_message("요청하신 리뷰를 찾을 수 없습니다.").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("리뷰를 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 리뷰 수정: 작성자만 가능
    @extend_schema(**ReviewSchema.update_review())
    def put(self, request, review_id):
        try:
            review = SubscriptionReview.objects.get(id=review_id)
            self.check_object_permissions(request, review)
            serializer = SubscriptionReviewSerializer(review, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response = SuccessResponseBuilder().with_message("리뷰 수정 성공").with_data({'review': serializer.data}).build()
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = ErrorResponseBuilder().with_message("입력 정보가 올바르지 않습니다.").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except SubscriptionReview.DoesNotExist:
            response = ErrorResponseBuilder().with_message("요청하신 리뷰를 찾을 수 없습니다.").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("리뷰를 수정하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 리뷰 삭제: 작성자만 가능
    @extend_schema(**ReviewSchema.delete_review())
    def delete(self, request, review_id):
        try:
            review = SubscriptionReview.objects.get(id=review_id)
            self.check_object_permissions(request, review)
            review.delete()
            response = SuccessResponseBuilder().with_message("리뷰 삭제 성공").build()
            return Response(response, status=status.HTTP_204_NO_CONTENT)
        except SubscriptionReview.DoesNotExist:
            response = ErrorResponseBuilder().with_message("요청하신 리뷰를 찾을 수 없습니다.").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("리뷰를 삭제하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 리뷰 좋아요 추가 API
class ReviewLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    # 리뷰 좋아요 여부 조회
    @extend_schema(**ReviewSchema.get_review_like_status())
    def get(self, request, review_id):
        try:
            review = SubscriptionReview.objects.get(id=review_id)
            liked = SubscriptionReviewLike.objects.filter(user=request.user, review=review).exists()
            response = SuccessResponseBuilder().with_message("리뷰 좋아요 여부 조회 성공").with_data({'liked': liked}).build()
            return Response(response, status=status.HTTP_200_OK)
            
        except Model.DoesNotExist:
            response = ErrorResponseBuilder().with_message("요청하신 리뷰를 찾을 수 없습니다.").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("리뷰 좋아요 상태를 확인하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 리뷰 좋아요 추가
    @extend_schema(**ReviewSchema.add_review_like())
    def post(self, request, review_id):
        try:
            review = SubscriptionReview.objects.get(id=review_id)
            SubscriptionReviewLike.objects.get_or_create(user=request.user, review=review)
            response = SuccessResponseBuilder().with_message("리뷰 좋아요 추가 성공").with_data({'message': 'liked'}).build()
            return Response(response, status=status.HTTP_200_OK)
                
        except Model.DoesNotExist:
            response = ErrorResponseBuilder().with_message("요청하신 리뷰를 찾을 수 없습니다.").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("리뷰 좋아요를 추가하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 리뷰 좋아요 취소
    @extend_schema(**ReviewSchema.remove_review_like())
    def delete(self, request, review_id):
        try:
            review = SubscriptionReview.objects.get(id=review_id)
            SubscriptionReviewLike.objects.filter(user=request.user, review=review).delete()
            response = SuccessResponseBuilder().with_message("리뷰 좋아요 취소 성공").with_data({'message': 'UnLiked'}).build()
            return Response(response, status=status.HTTP_200_OK)
                
        except Model.DoesNotExist:
            response = ErrorResponseBuilder().with_message("요청하신 리뷰를 찾을 수 없습니다.").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("리뷰 좋아요를 취소하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Model Request APIs
# <-------------------------------------------------------------------------------------------------------------------------------->
# Model Request 추가 API
class ModelRequestAPIView(APIView):
    permission_classes = [IsCIVerified]

    @extend_schema(**GarageSchema.create_model_request())
    def post(self, request):
        try:
            serializer = SubscriptionModelRequestSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                response = SuccessResponseBuilder().with_message("모델 요청 추가 성공").with_data({'model_request': serializer.data}).build()
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = ErrorResponseBuilder().with_message("입력 정보가 올바르지 않습니다.").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("모델 요청을 추가하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)