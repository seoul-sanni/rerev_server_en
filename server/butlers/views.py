# butlers/views.py
app_name = 'butlers'

from collections import defaultdict

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Prefetch, Q

from drf_spectacular.utils import extend_schema

from server.utils import SuccessResponseBuilder, ErrorResponseBuilder
from cars.models import Brand, Model, Car

from .task import send_butler_email
from .models import Butler, ButlerRequest, ButlerLike, ButlerReview, ButlerReviewLike, ButlerCoupon, ButlerUserCoupon
from .serializers import ButlerModelListSerializer, ButlerModelDetailSerializer, ButlerCarDetailSerializer, SimpleButlerModelSerializer
from .serializers import ButlerSerializer, ButlerRequestSerializer
from .serializers import ButlerReviewSerializer, ButlerReviewDetailSerializer, ButlerModelRequestSerializer
from .serializers import ButlerCouponSerializer, ButlerUserCouponSerializer
from .permissions import AllowAny, IsAuthenticated, IsCIVerified, IsAuthor, IsButlered
from .paginations import ButlerPagination
from .schemas import GarageSchema, CouponSchema, ButlerSchema, ReviewSchema

# Garage APIs
# <-------------------------------------------------------------------------------------------------------------------------------->
# Garage 목록을 조회하는 API
class GarageAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class = ButlerPagination

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
                'model_list': SimpleButlerModelSerializer(models, many=True).data
            }
            garage_list.append(garage_item)
        
        brands = request.query_params.getlist('brand')
        models = request.query_params.getlist('model')
        dates = request.query_params.getlist('date')
        order = request.query_params.get('order')

        try:
            cars_queryset = Car.objects.filter(is_active=True, is_butler=True).select_related('model', 'model__brand')

            # (brand OR model) AND (date)
            if brands or models:
                filter_conditions = Q()
                if brands:
                    filter_conditions |= Q(model__brand__slug__in=brands)
                if models:
                    filter_conditions |= Q(model__slug__in=models)
                cars_queryset = cars_queryset.filter(filter_conditions)
            
            if dates:
                exclude_conditions = Q()
                for date in dates:
                    exclude_conditions |= Q(butler_reservated_dates__contains=[date])
                cars_queryset = cars_queryset.exclude(exclude_conditions)
            
            if order == 'desc':
                sort_field = f'-{'butler_price'}'
            else:
                sort_field = 'butler_price'

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
                    'cars': ButlerCarDetailSerializer(page, many=True).data,
                    'pagination_info': pagination_info
                }
                response = SuccessResponseBuilder().with_message("차고 목록 조회 성공").with_data(response_data).build()
                return Response(response, status=status.HTTP_200_OK)
                
            else:
                response_data = {
                    'garage_list': garage_list,
                    'cars': ButlerCarDetailSerializer(cars_queryset, many=True).data,
                }    
                response = SuccessResponseBuilder().with_message("차고 목록 조회 성공").with_data(response_data).build()
                return Response(response, status=status.HTTP_200_OK)
                
        except Exception as e:
            response = ErrorResponseBuilder().with_message("차고 목록을 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 버틀러 가능한 자동차 모델 목록을 조회하는 API
class ModelListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(**GarageSchema.get_model_list())
    def get(self, request):
        try:
            models = Model.objects.filter(cars__is_active=True, cars__is_butler=True
            ).select_related('brand'
            ).prefetch_related(Prefetch('cars', queryset=Car.objects.filter(is_active=True, is_butler=True).prefetch_related('butler_requests', 'butler_requests__butlers'))
            ).distinct(
            ).order_by('brand__name', 'name')
            
            serializer = ButlerModelListSerializer(models, many=True)
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
            model = Model.objects.filter(id=model_id, cars__is_active=True, cars__is_butler=True
            ).select_related('brand'
            ).prefetch_related(Prefetch('cars', queryset=Car.objects.filter(is_active=True, is_butler=True).prefetch_related('butler_requests', 'butler_requests__butlers'))
            ).first()
            
            if not model:
                response = ErrorResponseBuilder().with_message("요청하신 모델을 찾을 수 없거나 버틀러 서비스가 불가능합니다.").build()
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            
            serializer = ButlerModelDetailSerializer(model)
            response = SuccessResponseBuilder().with_message("모델 상세 정보 조회 성공").with_data({'model': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)
            
        except Exception as e:
            response = ErrorResponseBuilder().with_message("모델 상세 정보를 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 버틀러 가능한 자동차 목록을 조회하는 API
class CarListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(**GarageSchema.get_car_list())
    def get(self, request):
        try:            
            cars = Car.objects.filter(is_active=True, is_butler=True).select_related('model', 'model__brand')
            serializer = ButlerCarDetailSerializer(cars, many=True)
            
            response = SuccessResponseBuilder().with_message("차량 목록 조회 성공").with_data({'cars': serializer.data}).build()
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
            car = Car.objects.filter(id=car_id, is_active=True, is_butler=True
            ).select_related('model', 'model__brand'
            ).first()
            
            if not car:
                response = ErrorResponseBuilder().with_message("요청하신 차량을 찾을 수 없거나 버틀러 서비스가 불가능합니다.").build()
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            
            serializer = ButlerCarDetailSerializer(car)
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
            user_coupons = ButlerUserCoupon.objects.filter(user=request.user)
            serializer = ButlerUserCouponSerializer(user_coupons, many=True)
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
            coupon = ButlerCoupon.objects.get(code=coupon_code)
            serializer = ButlerCouponSerializer(coupon)
            response = SuccessResponseBuilder().with_message("쿠폰 상세 정보 조회 성공").with_data({'coupon': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("쿠폰 정보를 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @extend_schema(**CouponSchema.add_coupon())
    def post(self, request, coupon_code):
        try:
            coupon = ButlerCoupon.objects.get(code=coupon_code)
            serializer = ButlerUserCouponSerializer(data=request.data)
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


# Butler APIs
# <-------------------------------------------------------------------------------------------------------------------------------->
# Butler 요청 정보를 조회하는 API
class ButlerRequestListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**ButlerSchema.get_butler_request_list())
    def get(self, request):
        try:
            butler_requests = ButlerRequest.objects.filter(user=request.user, is_active=True).select_related('car', 'car__model', 'car__model__brand')
            serializer = ButlerRequestSerializer(butler_requests, many=True)
            response = SuccessResponseBuilder().with_message("버틀러 요청 목록 조회 성공").with_data({'butler_requests': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("버틀러 요청 목록을 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Butler 요청 API
class ButlerRequestAPIView(APIView):
    permission_classes = [IsCIVerified]

    @extend_schema(**ButlerSchema.create_butler_request())
    def post(self, request, car_id):
        try:
            serializer = ButlerRequestSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, car_id=car_id)
                send_butler_email.delay("seobioh@gmail.com", serializer.data)
                response = SuccessResponseBuilder().with_message("버틀러 요청 추가 성공").with_data({'butler_request': serializer.data}).build()
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = ErrorResponseBuilder().with_message("입력 정보가 올바르지 않습니다.").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Car.DoesNotExist:
            response = ErrorResponseBuilder().with_message("요청하신 차량을 찾을 수 없습니다.").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("버틀러 요청을 추가하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Butler 정보를 조회하는 API
class ButlerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**ButlerSchema.get_butler_list())
    def get(self, request):
        try:
            butlers = Butler.objects.filter(request__user=request.user).select_related('request', 'request__user', 'request__car', 'request__car__model', 'request__car__model__brand')
            serializer = ButlerSerializer(butlers, many=True)
            response = SuccessResponseBuilder().with_message("버틀러 목록 조회 성공").with_data({'butlers': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("버틀러 목록을 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
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
            liked = ButlerLike.objects.filter(user=request.user, model=model).exists()
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
            ButlerLike.objects.get_or_create(user=request.user, model=model)
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
            ButlerLike.objects.filter(user=request.user, model=model).delete()
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
            reviews = ButlerReview.objects.all()
            serializer = ButlerReviewSerializer(reviews, many=True)
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
            return [IsButlered()]

    @extend_schema(**ReviewSchema.get_review_list())
    def get(self, request, model_id):
        try:
            reviews = ButlerReview.objects.filter(model_id=model_id)
            serializer = ButlerReviewSerializer(reviews, many=True)
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
            serializer = ButlerReviewSerializer(data=request.data)
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
            review = ButlerReview.objects.get(id=review_id)
            self.check_object_permissions(request, review)
            serializer = ButlerReviewDetailSerializer(review, context={'request': request})
            response = SuccessResponseBuilder().with_message("리뷰 상세 조회 성공").with_data({'review': serializer.data}).build()
            return Response(response, status=status.HTTP_200_OK)
        except ButlerReview.DoesNotExist:
            response = ErrorResponseBuilder().with_message("요청하신 리뷰를 찾을 수 없습니다.").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("리뷰를 불러오는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 리뷰 수정: 작성자만 가능
    @extend_schema(**ReviewSchema.update_review())
    def put(self, request, review_id):
        try:
            review = ButlerReview.objects.get(id=review_id)
            self.check_object_permissions(request, review)
            serializer = ButlerReviewSerializer(review, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response = SuccessResponseBuilder().with_message("리뷰 수정 성공").with_data({'review': serializer.data}).build()
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = ErrorResponseBuilder().with_message("입력 정보가 올바르지 않습니다.").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except ButlerReview.DoesNotExist:
            response = ErrorResponseBuilder().with_message("요청하신 리뷰를 찾을 수 없습니다.").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("리뷰를 수정하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 리뷰 삭제: 작성자만 가능
    @extend_schema(**ReviewSchema.delete_review())
    def delete(self, request, review_id):
        try:
            review = ButlerReview.objects.get(id=review_id)
            self.check_object_permissions(request, review)
            review.delete()
            response = SuccessResponseBuilder().with_message("리뷰 삭제 성공").build()
            return Response(response, status=status.HTTP_204_NO_CONTENT)
        except ButlerReview.DoesNotExist:
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
            review = ButlerReview.objects.get(id=review_id)
            liked = ButlerReviewLike.objects.filter(user=request.user, review=review).exists()
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
            review = ButlerReview.objects.get(id=review_id)
            ButlerReviewLike.objects.get_or_create(user=request.user, review=review)
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
            review = ButlerReview.objects.get(id=review_id)
            ButlerReviewLike.objects.filter(user=request.user, review=review).delete()
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
            serializer = ButlerModelRequestSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                response = SuccessResponseBuilder().with_message("버틀러 모델 요청 추가 성공").with_data({'model_request': serializer.data}).build()
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = ErrorResponseBuilder().with_message("입력 정보가 올바르지 않습니다.").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("버틀러 모델 요청을 추가하는 중 오류가 발생했습니다.").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)