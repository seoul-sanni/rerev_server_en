# buttlers/views.py
app_name = 'buttlers'

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db.models import Prefetch

from cars.models import Model, Car
from server.utils import ErrorResponseBuilder

from .task import send_buttler_email
from .models import Buttler, ButtlerRequest, ButtlerLike, ButtlerReview, ButtlerReviewLike, ButtlerCoupon, ButtlerUserCoupon
from .serializers import ButtlerModelListSerializer, ButtlerModelDetailSerializer, ButtlerCarDetailSerializer
from .serializers import ButtlerSerializer, ButtlerRequestSerializer
from .serializers import ButtlerReviewSerializer, ButtlerReviewDetailSerializer, ButtlerModelRequestSerializer
from .serializers import ButtlerCouponSerializer, ButtlerUserCouponSerializer
from .permissions import AllowAny, IsAuthenticated, IsCIVerified, IsAuthor, IsButtled

# 구독 가능한 자동차 모델 목록을 조회하는 API
class ModelListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            models = Model.objects.filter(
                cars__is_active=True,
                cars__is_buttler=True
            ).select_related('brand').prefetch_related(
                Prefetch(
                    'cars',
                    queryset=Car.objects.filter(
                        is_active=True,
                        is_buttler=True
                    ).prefetch_related('buttler_requests', 'buttler_requests__buttlers')
                )
            ).distinct().order_by('brand__name', 'name')
            
            serializer = ButtlerModelListSerializer(models, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to get model list").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 특정 자동차 모델의 상세 정보를 조회하는 API
class ModelDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, model_id):
        try:
            model = Model.objects.filter(
                id=model_id,
                cars__is_active=True,
                cars__is_buttler=True
            ).select_related('brand').prefetch_related(
                'cars', 'cars__buttler_requests', 'cars__buttler_requests__buttlers'
            ).first()
            
            if not model:
                response = ErrorResponseBuilder().with_message("Model not found or not buttler").build()
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            
            serializer = ButtlerModelDetailSerializer(model)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to get model detail").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 구독 가능한 자동차 목록을 조회하는 API
class CarListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            cars = Car.objects.filter(
                is_active=True,
                is_buttler=True
            ).select_related('model', 'model__brand').order_by('model__brand__name', 'model__name')
            
            serializer = ButtlerCarDetailSerializer(cars, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to get car list").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 특정 자동차의 상세 정보를 조회하는 API
class CarDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, car_id):
        try:
            car = Car.objects.filter(
                id=car_id,
                is_active=True,
                is_buttler=True
            ).select_related('model', 'model__brand').first()
            
            if not car:
                response = ErrorResponseBuilder().with_message("Car not found or not buttler").build()
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            
            serializer = ButtlerCarDetailSerializer(car)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to get car detail").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Coupon APIs
# <-------------------------------------------------------------------------------------------------------------------------------->
# Coupon 목록을 조회하는 API
class CouponListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_coupons = ButtlerUserCoupon.objects.filter(user=request.user)
            serializer = ButtlerUserCouponSerializer(user_coupons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to get user coupons").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CouponDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, coupon_code):
        try:
            coupon = ButtlerCoupon.objects.get(code=coupon_code)
            serializer = ButtlerCouponSerializer(coupon)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to get coupon").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, coupon_code):
        try:
            coupon = ButtlerCoupon.objects.get(code=coupon_code)
            serializer = ButtlerUserCouponSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, coupon=coupon)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                response = ErrorResponseBuilder().with_message("Validation failed").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to add user coupon").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 구독 APIs
# <-------------------------------------------------------------------------------------------------------------------------------->
# 구독 요청 정보를 조회하는 API
class ButtlerRequestListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            buttler_requests = ButtlerRequest.objects.filter(user=request.user, is_active=True).select_related('car', 'car__model', 'car__model__brand')
            serializer = ButtlerRequestSerializer(buttler_requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to get buttler requests").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 구독 요청 API
class ButtlerRequestAPIView(APIView):
    permission_classes = [IsCIVerified]

    def post(self, request, car_id):
        try:
            serializer = ButtlerRequestSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, car_id=car_id)
                send_buttler_email.delay("seobioh@gmail.com", serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                response = ErrorResponseBuilder().with_message("Validation failed").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Car.DoesNotExist:
            response = ErrorResponseBuilder().with_message("Car not found").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to add buttler request").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 구독 정보를 조회하는 API
class ButtlerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            buttlers = Buttler.objects.filter(request__user=request.user).select_related('request', 'request__user', 'request__car', 'request__car__model', 'request__car__model__brand')
            serializer = ButtlerSerializer(buttlers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to get buttlers").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 좋아요 APIs
# <-------------------------------------------------------------------------------------------------------------------------------->
# 좋아요 추가 API
class LikeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    # 모델 좋아요 여부 조회
    def get(self, request, model_id):
        try:
            model = Model.objects.get(id=model_id)
            liked = ButtlerLike.objects.filter(user=request.user, model=model).exists()
            return Response({'liked': liked}, status=status.HTTP_200_OK)

        except Model.DoesNotExist:
            response = ErrorResponseBuilder().with_message("Model not found").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to check like status").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 모델 좋아요 추가
    def post(self, request, model_id):
        try:
            model = Model.objects.get(id=model_id)
            ButtlerLike.objects.get_or_create(user=request.user, model=model)
            return Response({'message': 'Liked'}, status=status.HTTP_200_OK)
                
        except Model.DoesNotExist:
            response = ErrorResponseBuilder().with_message("Model not found").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to add like").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 모델 좋아요 취소
    def delete(self, request, model_id):
        try:
            model = Model.objects.get(id=model_id)
            ButtlerLike.objects.filter(user=request.user, model=model).delete()
            return Response({'message': 'UnLiked'}, status=status.HTTP_200_OK)
                
        except Model.DoesNotExist:
            response = ErrorResponseBuilder().with_message("Model not found").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to remove like").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 리뷰 APIs
# <-------------------------------------------------------------------------------------------------------------------------------->
# 모든 리뷰 목록을 조회하는 API
class ReviewListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            reviews = ButtlerReview.objects.all()
            serializer = ButtlerReviewSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to get reviews").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 리뷰 추가 API
class ReviewAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        else :
            return [IsButtled()]

    def get(self, request, model_id):
        try:
            reviews = ButtlerReview.objects.filter(model_id=model_id)
            serializer = ButtlerReviewSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to get reviews").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, model_id):
        try:
            model = Model.objects.get(id=model_id)
            self.check_object_permissions(request, model)
            serializer = ButtlerReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, model_id=model_id)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                response = ErrorResponseBuilder().with_message("Validation failed").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to add review").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 리뷰 조회 API
class ReviewDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        else :
            return [IsAuthor()]

    # 리뷰 상세 조회
    def get(self, request, review_id):
        try:
            review = ButtlerReview.objects.get(id=review_id)
            self.check_object_permissions(request, review)
            serializer = ButtlerReviewDetailSerializer(review, context={'request': request})
            return Response(serializer.data)
        except ButtlerReview.DoesNotExist:
            response = ErrorResponseBuilder().with_message("Review not found").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to get review").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 리뷰 수정: 작성자만 가능
    def put(self, request, review_id):
        try:
            review = ButtlerReview.objects.get(id=review_id)
            self.check_object_permissions(request, review)
            serializer = ButtlerReviewSerializer(review, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                response = ErrorResponseBuilder().with_message("Validation failed").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except ButtlerReview.DoesNotExist:
            response = ErrorResponseBuilder().with_message("Review not found").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to update review").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 리뷰 삭제: 작성자만 가능
    def delete(self, request, review_id):
        try:
            review = ButtlerReview.objects.get(id=review_id)
            self.check_object_permissions(request, review)
            review.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ButtlerReview.DoesNotExist:
            response = ErrorResponseBuilder().with_message("Review not found").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to delete review").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 리뷰 좋아요 추가 API
class ReviewLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    # 리뷰 좋아요 여부 조회
    def get(self, request, review_id):
        try:
            review = ButtlerReview.objects.get(id=review_id)
            liked = ButtlerReviewLike.objects.filter(user=request.user, review=review).exists()
            return Response({'liked': liked})
            
        except Model.DoesNotExist:
            response = ErrorResponseBuilder().with_message("Model not found").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to check like status").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 리뷰 좋아요 추가
    def post(self, request, review_id):
        try:
            review = ButtlerReview.objects.get(id=review_id)
            ButtlerReviewLike.objects.get_or_create(user=request.user, review=review)
            return Response({'message': 'liked'}, status=status.HTTP_200_OK)
                
        except Model.DoesNotExist:
            response = ErrorResponseBuilder().with_message("Model not found").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to add like").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 리뷰 좋아요 취소
    def delete(self, request, review_id):
        try:
            review = ButtlerReview.objects.get(id=review_id)
            ButtlerReviewLike.objects.filter(user=request.user, review=review).delete()
            return Response({'message': 'UnLiked'}, status=status.HTTP_200_OK)
                
        except Model.DoesNotExist:
            response = ErrorResponseBuilder().with_message("Model not found").build()
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to remove like").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Model Request APIs
# <-------------------------------------------------------------------------------------------------------------------------------->
# Model Request 추가 API
class ModelRequestAPIView(APIView):
    permission_classes = [IsCIVerified]

    def post(self, request):
        try:
            serializer = ButtlerModelRequestSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                response = ErrorResponseBuilder().with_message("Validation failed").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("Failed to add model request").with_errors(str(e)).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)