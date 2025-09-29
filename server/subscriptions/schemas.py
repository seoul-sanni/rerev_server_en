# subscriptions/schemas.py
app_name = "subscriptions"

from rest_framework import serializers

from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes

from server.schemas import SuccessResponseSerializer, ErrorResponseSerializer

# Common Examples
# <-------------------------------------------------------------------------------------------------------------------------------->
class CommonExamples:
    @staticmethod
    def success_example(message="요청이 성공적으로 처리되었습니다.", data=None):
        """일반 성공 응답 예시"""
        if data is None:
            data = {"result": "success"}
        
        return OpenApiExample(
            "Success Response",
            summary="성공",
            description="요청이 성공적으로 처리된 경우의 응답",
            value={
                "code": 0,
                "message": message,
                "data": data
            },
            response_only=True,
            status_codes=['200']
        )
    
    @staticmethod
    def error_example(message="요청 처리 중 오류가 발생했습니다.", errors=None):
        """일반 오류 응답 예시"""
        if errors is None:
            errors = {"detail": "요청을 처리할 수 없습니다."}
        
        return OpenApiExample(
            "Error Response",
            summary="실패",
            description="요청 처리 중 오류가 발생한 경우의 응답",
            value={
                "code": 1,
                "message": message,
                "errors": errors
            },
            response_only=True,
            status_codes=['400', '500']
        )


# Wrapper Serializers
# <-------------------------------------------------------------------------------------------------------------------------------->
class SubscriptionRequestCreateSerializer(serializers.Serializer):
    month = serializers.IntegerField(help_text="구독 개월 수")
    coupon_id = serializers.IntegerField(required=False, allow_null=True, help_text="쿠폰 ID")
    point_amount = serializers.IntegerField(required=False, allow_null=True, help_text="사용할 포인트 금액")
    billing_key = serializers.CharField(help_text="결제 키")


class CouponAddSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(help_text="쿠폰 코드")


class ReviewCreateSerializer(serializers.Serializer):
    content = serializers.CharField(help_text="리뷰 내용")
    image = serializers.CharField(required=False, allow_blank=True, help_text="리뷰 이미지 URL")


class ModelRequestCreateSerializer(serializers.Serializer):
    model = serializers.CharField(help_text="요청할 모델명")


class LikeResponseSerializer(serializers.Serializer):
    liked = serializers.BooleanField(help_text="좋아요 여부")


class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="응답 메시지")


# Garage Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class GarageSchema:
    @staticmethod
    def get_garage():
        return {
            'summary': "차고 목록 조회",
            'description': "구독 가능한 차량 목록을 조회합니다. 브랜드, 모델-슬러그, 개월수로 필터링할 수 있습니다.",
            'parameters': [
                OpenApiParameter(
                    name="brand",
                    type=OpenApiTypes.STR,
                    location=OpenApiParameter.QUERY,
                    description="브랜드 슬러그로 필터링 (여러 개 가능)",
                    many=True,  # <-- 중요 (배열 파라미터)
                    examples=[OpenApiExample("브랜드 예시", value=["bmw", "tesla"])]
                ),
                OpenApiParameter(
                    name="model",
                    type=OpenApiTypes.STR,
                    location=OpenApiParameter.QUERY,
                    description="모델 슬러그로 필터링 (여러 개 가능)",
                    many=True,
                    examples=[OpenApiExample("모델 예시", value=["bmw-x5-bmw_x5", "tesla-model3-tesla_model3"])]
                ),
                OpenApiParameter(
                    name="month",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.QUERY,
                    description="구독 개월수로 필터링 (여러 개 가능)",
                    many=True,
                    examples=[OpenApiExample("개월수 예시", value=[12, 24, 36])]
                ),
                OpenApiParameter(
                    name="sort",
                    type=OpenApiTypes.STR,
                    location=OpenApiParameter.QUERY,
                    description="정렬 기준 필드",
                    enum=["subscription_available_from", "subscription_fee_minimum", "mileage", "release_date"],
                    examples=[OpenApiExample("정렬 예시", value="subscription_fee_minimum")]
                ),
                OpenApiParameter(
                    name="order",
                    type=OpenApiTypes.STR,
                    location=OpenApiParameter.QUERY,
                    description="정렬 방향",
                    enum=["asc", "desc"],
                    default="asc",
                    examples=[OpenApiExample("정렬 방향 예시", value="desc")]
                ),
                OpenApiParameter(
                    name="available_only",
                    type=OpenApiTypes.BOOL,
                    location=OpenApiParameter.QUERY,
                    description="구독 가능한 상품만 표시",
                    examples=[OpenApiExample("사용 예시", value=True)]
                ),
            ],
            'responses': {
                200: SuccessResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="차고 목록 조회 성공",
                    data={
                        "garage_list": [
                            {
                                "name": "BMW",
                                "slug": "bmw",
                                "model_list": [
                                    {
                                        "id": 3,
                                        "name": "X5",
                                        "image": "https://example.com/x5.jpg",
                                        "code": "BMW_X5",
                                        "slug": "bmw-x5-bmw_x5",
                                        "car_count": 5
                                    },
                                    {
                                        "id": 4,
                                        "name": "X3",
                                        "image": "https://example.com/x3.jpg",
                                        "code": "BMW_X3",
                                        "slug": "bmw-x3-bmw_x3",
                                        "car_count": 3
                                    }
                                ]
                            },
                            {
                                "name": "Tesla",
                                "slug": "tesla",
                                "model_list": [
                                    {
                                        "id": 1,
                                        "name": "Model 3",
                                        "image": "https://example.com/model3.jpg",
                                        "code": "TESLA_MODEL3",
                                        "slug": "tesla-model3-tesla_model3",
                                        "car_count": 8
                                    },
                                    {
                                        "id": 2,
                                        "name": "Model Y",
                                        "image": "https://example.com/modely.jpg",
                                        "code": "TESLA_MODELY",
                                        "slug": "tesla-modely-tesla_modely",
                                        "car_count": 2
                                    }
                                ]
                            }
                        ],
                        "cars": [
                            {
                                "id": 1,
                                "model": {
                                    "id": 1,
                                    "name": "Model 3",
                                    "brand": {
                                        "id": 1,
                                        "name": "Tesla"
                                    }
                                },
                                "subscription_fee_1": 500000,
                                "subscription_fee_3": 450000,
                                "subscription_fee_6": 400000,
                                "subscription_fee_12": 350000,
                                "is_new": True,
                                "is_hot": False,
                                "is_buttler": False,
                                "buttler_price": 0,
                                "color": "White",
                                "sub_model": "Standard",
                                "trim": "Long Range",
                                "inspection_report": "https://example.com/report.pdf"
                            }
                        ],
                        "pagination_info": {
                            "count": 50,
                            "next": "http://api.example.com/garage/?page=2",
                            "previous": None,
                            "page_size": 20,
                            "current_page": 1,
                            "total_pages": 3
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="차고 목록을 불러오는 중 오류가 발생했습니다.",
                    errors={"detail": "Database connection error"}
                )
            ]
        }
    
    @staticmethod
    def get_model_list():
        return {
            'summary': "모델 목록 조회",
            'description': "구독 가능한 자동차 모델 목록을 조회합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="모델 목록 조회 성공",
                    data={
                        "models": [
                            {
                                "id": 1,
                                "name": "Model 3",
                                "brand": {
                                    "id": 1,
                                    "name": "Tesla"
                                },
                                "cars": [
                                    {
                                        "id": 1,
                                        "subscription_fee_1": 500000,
                                        "subscription_fee_3": 450000,
                                        "subscription_fee_6": 400000,
                                        "subscription_fee_12": 350000,
                                        "subscription_fee_minimum": 500000,
                                        "subscription_available_from": "2024-01-01",
                                        "is_new": True,
                                        "is_hot": False
                                    }
                                ],
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="모델 목록을 불러오는 중 오류가 발생했습니다.",
                    errors={"detail": "Database connection error"}
                )
            ]
        }
    
    @staticmethod
    def get_model_detail():
        return {
            'summary': "모델 상세 정보 조회",
            'description': "특정 자동차 모델의 상세 정보를 조회합니다.",
            'operation_id': 'subscriptions_models_detail',
            'responses': {
                200: SuccessResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="모델 상세 정보 조회 성공",
                    data={
                        "model": {
                            "id": 1,
                            "name": "Model 3",
                            "brand": {
                                "id": 1,
                                "name": "Tesla"
                            },
                            "cars": [
                                {
                                    "id": 1,
                                    "subscription_fee_1": 500000,
                                    "subscription_fee_3": 450000,
                                    "subscription_fee_6": 400000,
                                    "subscription_fee_12": 350000,
                                    "is_new": True,
                                    "is_hot": False,
                                    "is_buttler": False,
                                    "buttler_price": 0,
                                    "color": "White",
                                    "sub_model": "Standard",
                                    "trim": "Long Range",
                                    "inspection_report": "https://example.com/report.pdf"
                                }
                            ],
                            "subscription_requests_count": 5,
                            "subscriptions_count": 3
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="요청하신 모델을 찾을 수 없거나 구독이 불가능합니다.",
                    errors={"detail": "Model not found"}
                )
            ]
        }
    
    @staticmethod
    def get_car_list():
        return {
            'summary': "차량 목록 조회",
            'description': "구독 가능한 자동차 목록을 조회합니다. 신차, 인기차, 구독 종료 예정 차량으로 분류됩니다.",
            'responses': {
                200: SuccessResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="차량 목록 조회 성공",
                    data={
                        "new_cars": [
                            {
                                "id": 1,
                                "model": {
                                    "id": 1,
                                    "name": "Model 3",
                                    "brand": {
                                        "id": 1,
                                        "name": "Tesla"
                                    }
                                },
                                "subscription_fee_1": 500000,
                                "subscription_fee_3": 450000,
                                "subscription_fee_6": 400000,
                                "subscription_fee_12": 350000,
                                "is_new": True,
                                "is_hot": False,
                                "is_buttler": False,
                                "buttler_price": 0,
                                "color": "White",
                                "sub_model": "Standard",
                                "trim": "Long Range",
                                "inspection_report": "https://example.com/report.pdf"
                            }
                        ],
                        "hot_cars": [
                            {
                                "id": 2,
                                "model": {
                                    "id": 2,
                                    "name": "Model Y",
                                    "brand": {
                                        "id": 1,
                                        "name": "Tesla"
                                    }
                                },
                                "subscription_fee_1": 600000,
                                "subscription_fee_3": 550000,
                                "subscription_fee_6": 500000,
                                "subscription_fee_12": 450000,
                                "is_new": False,
                                "is_hot": True,
                                "is_buttler": False,
                                "buttler_price": 0,
                                "color": "Black",
                                "sub_model": "Performance",
                                "trim": "Long Range",
                                "inspection_report": "https://example.com/report2.pdf"
                            }
                        ],
                        "upcoming_cars": [
                            {
                                "id": 3,
                                "model": {
                                    "id": 3,
                                    "name": "Model S",
                                    "brand": {
                                        "id": 1,
                                        "name": "Tesla"
                                    }
                                },
                                "subscription_fee_1": 800000,
                                "subscription_fee_3": 750000,
                                "subscription_fee_6": 700000,
                                "subscription_fee_12": 650000,
                                "is_new": False,
                                "is_hot": False,
                                "is_buttler": True,
                                "buttler_price": 100000,
                                "color": "Red",
                                "sub_model": "Plaid",
                                "trim": "Performance",
                                "inspection_report": "https://example.com/report3.pdf"
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="차량 목록을 불러오는 중 오류가 발생했습니다.",
                    errors={"detail": "Database connection error"}
                )
            ]
        }
    
    @staticmethod
    def get_car_detail():
        return {
            'summary': "차량 상세 정보 조회",
            'description': "특정 자동차의 상세 정보를 조회합니다.",
            'operation_id': 'subscriptions_cars_detail',
            'responses': {
                200: SuccessResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="차량 상세 정보 조회 성공",
                    data={
                        "car": {
                            "id": 1,
                            "model": {
                                "id": 1,
                                "name": "Model 3",
                                "brand": {
                                    "id": 1,
                                    "name": "Tesla"
                                }
                            },
                            "subscription_fee_1": 500000,
                            "subscription_fee_3": 450000,
                            "subscription_fee_6": 400000,
                            "subscription_fee_12": 350000,
                            "subscription_fee_24": 300000,
                            "subscription_fee_36": 280000,
                            "subscription_fee_48": 260000,
                            "subscription_fee_60": 240000,
                            "subscription_fee_72": 220000,
                            "subscription_fee_84": 200000,
                            "subscription_fee_96": 180000,
                            "is_new": True,
                            "is_hot": False,
                            "is_buttler": False,
                            "buttler_price": 0,
                            "color": "White",
                            "sub_model": "Standard",
                            "trim": "Long Range",
                            "inspection_report": "https://example.com/report.pdf"
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="요청하신 차량을 찾을 수 없거나 구독이 불가능합니다.",
                    errors={"detail": "Car not found"}
                )
            ]
        }

    @staticmethod
    def create_model_request():
        return {
            'summary': "모델 요청 생성",
            'description': "새로운 모델 요청을 생성합니다. CI 인증이 필요합니다.",
            'request': ModelRequestCreateSerializer,
            'responses': {
                201: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="모델 요청 추가 성공",
                    data={
                        "model_request": {
                            "id": 1,
                            "user": 1,
                            "model": "BMW X5",
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z",
                            "is_active": True
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="입력 정보가 올바르지 않습니다.",
                    errors={"model": ["This field is required."]}
                ),
                CommonExamples.error_example(
                    message="모델 요청을 추가하는 중 오류가 발생했습니다.",
                    errors={"detail": "Database connection error"}
                )
            ]
        }

    @staticmethod
    def get_model_like_status():
        return {
            'summary': "모델 좋아요 여부 조회",
            'description': "특정 모델에 대한 사용자의 좋아요 여부를 조회합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="모델 좋아요 여부 조회 성공",
                    data={
                        "liked": True
                    }
                ),
                CommonExamples.error_example(
                    message="요청하신 모델을 찾을 수 없습니다.",
                    errors={"detail": "Model not found"}
                )
            ]
        }
    
    @staticmethod
    def add_model_like():
        return {
            'summary': "모델 좋아요 추가",
            'description': "특정 모델에 좋아요를 추가합니다.",
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="모델 좋아요 추가 성공",
                    data={
                        "message": "Liked"
                    }
                ),
                CommonExamples.error_example(
                    message="요청하신 모델을 찾을 수 없습니다.",
                    errors={"detail": "Model not found"}
                )
            ]
        }
    
    @staticmethod
    def remove_model_like():
        return {
            'summary': "모델 좋아요 취소",
            'description': "특정 모델의 좋아요를 취소합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="모델 좋아요 취소 성공",
                    data={
                        "message": "UnLiked"
                    }
                ),
                CommonExamples.error_example(
                    message="요청하신 모델을 찾을 수 없습니다.",
                    errors={"detail": "Model not found"}
                )
            ]
        }


# Coupon Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class CouponSchema:
    @staticmethod
    def get_coupon_list():
        return {
            'summary': "쿠폰 목록 조회",
            'description': "사용자의 쿠폰 목록을 조회합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="쿠폰 목록 조회 성공",
                    data={
                        "coupons": [
                            {
                                "id": 1,
                                "user": 1,
                                "coupon": {
                                    "id": 1,
                                    "code": "WELCOME10",
                                    "name": "신규 가입 할인",
                                    "description": "신규 가입자 10% 할인",
                                    "discount_type": "PERCENTAGE",
                                    "discount_rate": 10,
                                    "max_discount": 100000,
                                    "min_price": 0,
                                    "max_price": 1000000,
                                    "min_month": 1,
                                    "max_month": 12,
                                    "usage_limit": 100,
                                    "usage_limit_per_user": 1,
                                    "valid_from": "2024-01-01T00:00:00Z",
                                    "valid_to": "2024-12-31T23:59:59Z",
                                    "is_active": True
                                },
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z",
                                "used_at": None,
                                "is_active": True
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                )
            ]
        }
    
    @staticmethod
    def get_coupon_detail():
        return {
            'summary': "쿠폰 상세 정보 조회",
            'description': "특정 쿠폰의 상세 정보를 조회합니다.",
            'operation_id': 'subscriptions_coupons_detail',
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="쿠폰 상세 정보 조회 성공",
                    data={
                        "coupon": {
                            "id": 1,
                            "code": "WELCOME10",
                            "name": "신규 가입 할인",
                            "description": "신규 가입자 10% 할인",
                            "discount_type": "PERCENTAGE",
                            "discount_rate": 10,
                            "max_discount": 100000,
                            "min_price": 0,
                            "max_price": 1000000,
                            "min_month": 1,
                            "max_month": 12,
                            "usage_limit": 100,
                            "usage_limit_per_user": 1,
                            "valid_from": "2024-01-01T00:00:00Z",
                            "valid_to": "2024-12-31T23:59:59Z",
                            "is_active": True
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="쿠폰 정보를 불러오는 중 오류가 발생했습니다.",
                    errors={"detail": "Coupon not found"}
                )
            ]
        }
    
    @staticmethod
    def add_coupon():
        return {
            'summary': "쿠폰 추가",
            'description': "사용자에게 쿠폰을 추가합니다.",
            'request': CouponAddSerializer,
            'responses': {
                201: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="쿠폰 추가 성공",
                    data={
                        "coupon": {
                            "id": 1,
                            "user": 1,
                            "coupon": {
                                "id": 1,
                                "code": "WELCOME10",
                                "name": "신규 가입 할인",
                                "description": "신규 가입자 10% 할인",
                                "discount_type": "PERCENTAGE",
                                "discount_rate": 10,
                                "max_discount": 100000,
                                "min_price": 0,
                                "max_price": 1000000,
                                "min_month": 1,
                                "max_month": 12,
                                "usage_limit": 100,
                                "usage_limit_per_user": 1,
                                "valid_from": "2024-01-01T00:00:00Z",
                                "valid_to": "2024-12-31T23:59:59Z",
                                "is_active": True
                            },
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z",
                            "used_at": None,
                            "is_active": True
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="입력 정보가 올바르지 않습니다.",
                    errors={"coupon": ["This field is required."]}
                ),
                CommonExamples.error_example(
                    message="쿠폰을 추가하는 중 오류가 발생했습니다.",
                    errors={"detail": "Coupon already exists for user"}
                )
            ]
        }


# Subscription Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class SubscriptionSchema:
    @staticmethod
    def get_subscription_request_list():
        return {
            'summary': "구독 요청 목록 조회",
            'description': "사용자의 구독 요청 목록을 조회합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="구독 요청 목록 조회 성공",
                    data={
                        "subscription_requests": [
                            {
                                "id": 1,
                                "user": 1,
                                "car": {
                                    "id": 1,
                                    "model": {
                                        "id": 1,
                                        "name": "Model 3",
                                        "brand": {
                                            "id": 1,
                                            "name": "Tesla"
                                        }
                                    }
                                },
                                "start_date": "2024-01-01",
                                "month": 12,
                                "end_date": "2024-12-31",
                                "coupon": {
                                    "id": 1,
                                    "code": "WELCOME10",
                                    "name": "신규 가입 할인"
                                },
                                "point": {
                                    "id": 1,
                                    "amount": 50000,
                                    "transaction_type": "COUPON"
                                },
                                "billing_key": "billing_key_123",
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z",
                                "is_active": True
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                )
            ]
        }
    
    @staticmethod
    def create_subscription_request():
        return {
            'summary': "구독 요청 생성",
            'description': "특정 차량에 대한 구독 요청을 생성합니다. CI 인증이 필요합니다.",
            'request': SubscriptionRequestCreateSerializer,
            'responses': {
                201: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="구독 요청 추가 성공",
                    data={
                        "subscription_request": {
                            "id": 1,
                            "user": 1,
                            "car": 1,
                            "start_date": "2024-01-01",
                            "month": 12,
                            "end_date": "2024-12-31",
                            "coupon": 1,
                            "point": 1,
                            "billing_key": "billing_key_123",
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z",
                            "is_active": True
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="입력 정보가 올바르지 않습니다.",
                    errors={"month": ["This field is required."]}
                ),
                CommonExamples.error_example(
                    message="요청하신 차량을 찾을 수 없습니다.",
                    errors={"detail": "Car not found"}
                )
            ]
        }
    
    @staticmethod
    def get_subscription_request_detail():
        return {
            'summary': "구독 요청 상세 정보 조회",
            'description': "특정 구독 요청의 상세 정보를 조회합니다. 작성자만 조회 가능합니다.",
            'operation_id': 'subscriptions_subscription_request_detail',
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="구독 요청 상세 정보 조회 성공",
                    data={
                        "subscription_request": {
                            "id": 1,
                            "user": 1,
                            "car": {
                                "id": 1,
                                "model": {
                                    "id": 1,
                                    "name": "Model 3",
                                    "brand": {
                                        "id": 1,
                                        "name": "Tesla",
                                        "slug": "tesla",
                                        "image": "https://example.com/tesla.jpg"
                                    },
                                    "code": "TESLA_MODEL3",
                                    "image": "https://example.com/model3.jpg",
                                    "front_image": "https://example.com/model3_front.jpg",
                                    "rear_image": "https://example.com/model3_rear.jpg",
                                    "slug": "tesla-model3-tesla_model3"
                                },
                                "sub_model": "Standard",
                                "trim": "Long Range",
                                "color": "White",
                                "vin_number": "5YJ3E1EA4KF123456",
                                "license_plate": "12가3456",
                                "description": "Tesla Model 3 Long Range",
                                "images": ["https://example.com/car1.jpg", "https://example.com/car2.jpg"],
                                "inspection_report": "https://example.com/report.pdf",
                                "retail_price": 50000000,
                                "release_date": "2024-01-01",
                                "mileage": 1000,
                                "is_new": True,
                                "is_hot": False,
                                "is_sellable": True,
                                "sell_price": 45000000,
                                "is_subscriptable": True,
                                "subscription_fee_1": 500000,
                                "subscription_fee_3": 450000,
                                "subscription_fee_6": 400000,
                                "subscription_fee_12": 350000,
                                "subscription_fee_24": 300000,
                                "subscription_fee_36": 280000,
                                "subscription_fee_48": 260000,
                                "subscription_fee_60": 240000,
                                "subscription_fee_72": 220000,
                                "subscription_fee_84": 200000,
                                "subscription_fee_96": 180000,
                                "subscription_fee_minimum": 500000,
                                "subscription_available_from": "2024-01-01"
                            },
                            "month": 12,
                            "start_date": "2024-01-01",
                            "end_date": "2024-12-31",
                            "point_used": 50000,
                            "coupon": {
                                "id": 1,
                                "user": 1,
                                "coupon": {
                                    "id": 1,
                                    "code": "WELCOME10",
                                    "name": "신규 가입 할인",
                                    "description": "신규 가입자 10% 할인",
                                    "brand_ids": [1],
                                    "model_ids": [1],
                                    "car_ids": [1],
                                    "discount_type": "PERCENTAGE",
                                    "discount_rate": 10,
                                    "max_discount": 100000,
                                    "discount": 0,
                                    "min_price": 0,
                                    "max_price": 1000000,
                                    "min_month": 1,
                                    "max_month": 12,
                                    "valid_from": "2024-01-01T00:00:00Z",
                                    "valid_to": "2024-12-31T23:59:59Z",
                                    "is_specific": False
                                },
                                "is_active": True,
                                "is_used": False,
                                "is_valid": True,
                                "created_at": "2024-01-01T00:00:00Z",
                                "used_at": None
                            },
                            "customer_key": "customer_key_123",
                            "auth_key": "auth_key_123",
                            "billing_key": "billing_key_123",
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z",
                            "is_active": True
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="요청하신 구독 요청을 찾을 수 없습니다.",
                    errors={"detail": "Subscription request not found"}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "You do not have permission to perform this action."}
                )
            ]
        }
    
    @staticmethod
    def update_subscription_request():
        return {
            'summary': "구독 요청 수정",
            'description': "구독 요청 정보를 수정합니다. 작성자만 수정 가능합니다.",
            'request': SubscriptionRequestCreateSerializer,
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="구독 요청 상세 정보를 수정 성공",
                    data={
                        "subscription_request": {
                            "id": 1,
                            "user": 1,
                            "car": {
                                "id": 1,
                                "model": {
                                    "id": 1,
                                    "name": "Model 3",
                                    "brand": {
                                        "id": 1,
                                        "name": "Tesla",
                                        "slug": "tesla",
                                        "image": "https://example.com/tesla.jpg"
                                    },
                                    "code": "TESLA_MODEL3",
                                    "image": "https://example.com/model3.jpg",
                                    "front_image": "https://example.com/model3_front.jpg",
                                    "rear_image": "https://example.com/model3_rear.jpg",
                                    "slug": "tesla-model3-tesla_model3"
                                },
                                "sub_model": "Standard",
                                "trim": "Long Range",
                                "color": "White",
                                "vin_number": "5YJ3E1EA4KF123456",
                                "license_plate": "12가3456",
                                "description": "Tesla Model 3 Long Range",
                                "images": ["https://example.com/car1.jpg", "https://example.com/car2.jpg"],
                                "inspection_report": "https://example.com/report.pdf",
                                "retail_price": 50000000,
                                "release_date": "2024-01-01",
                                "mileage": 1000,
                                "is_new": True,
                                "is_hot": False,
                                "is_sellable": True,
                                "sell_price": 45000000,
                                "is_subscriptable": True,
                                "subscription_fee_1": 500000,
                                "subscription_fee_3": 450000,
                                "subscription_fee_6": 400000,
                                "subscription_fee_12": 350000,
                                "subscription_fee_24": 300000,
                                "subscription_fee_36": 280000,
                                "subscription_fee_48": 260000,
                                "subscription_fee_60": 240000,
                                "subscription_fee_72": 220000,
                                "subscription_fee_84": 200000,
                                "subscription_fee_96": 180000,
                                "subscription_fee_minimum": 500000,
                                "subscription_available_from": "2024-01-01"
                            },
                            "month": 24,
                            "start_date": "2024-02-01",
                            "end_date": "2026-01-31",
                            "point_used": 50000,
                            "coupon": {
                                "id": 1,
                                "user": 1,
                                "coupon": {
                                    "id": 1,
                                    "code": "WELCOME10",
                                    "name": "신규 가입 할인",
                                    "description": "신규 가입자 10% 할인",
                                    "brand_ids": [1],
                                    "model_ids": [1],
                                    "car_ids": [1],
                                    "discount_type": "PERCENTAGE",
                                    "discount_rate": 10,
                                    "max_discount": 100000,
                                    "discount": 0,
                                    "min_price": 0,
                                    "max_price": 1000000,
                                    "min_month": 1,
                                    "max_month": 12,
                                    "valid_from": "2024-01-01T00:00:00Z",
                                    "valid_to": "2024-12-31T23:59:59Z",
                                    "is_specific": False
                                },
                                "is_active": True,
                                "is_used": False,
                                "is_valid": True,
                                "created_at": "2024-01-01T00:00:00Z",
                                "used_at": None
                            },
                            "customer_key": "customer_key_123",
                            "auth_key": "auth_key_123",
                            "billing_key": "billing_key_123",
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-02T00:00:00Z",
                            "is_active": True
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="입력 정보가 올바르지 않습니다.",
                    errors={
                        "month": ["This field is required."],
                        "start_date": ["This field is required."]
                    }
                ),
                CommonExamples.error_example(
                    message="요청하신 구독 요청을 찾을 수 없습니다.",
                    errors={"detail": "Subscription request not found"}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "You do not have permission to perform this action."}
                )
            ]
        }
    
    @staticmethod
    def delete_subscription_request():
        return {
            'summary': "구독 요청 삭제",
            'description': "구독 요청을 삭제합니다. 작성자만 삭제 가능하며, 이미 진행중인 구독이 있는 경우 삭제할 수 없습니다.",
            'responses': {
                204: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="구독 요청 삭제 성공",
                    data={}
                ),
                CommonExamples.error_example(
                    message="이미 진행중인 구독입니다. 본사에 문의해주세요.",
                    errors={"detail": "Cannot delete request with active subscription"}
                ),
                CommonExamples.error_example(
                    message="요청하신 구독 요청을 찾을 수 없습니다.",
                    errors={"detail": "Subscription request not found"}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "You do not have permission to perform this action."}
                )
            ]
        }
    
    @staticmethod
    def get_subscription_list():
        return {
            'summary': "구독 목록 조회",
            'description': "사용자의 구독 목록을 조회합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="구독 목록 조회 성공",
                    data={
                        "subscriptions": [
                            {
                                "id": 1,
                                "request": {
                                    "id": 1,
                                    "user": {
                                        "id": 1,
                                        "username": "testuser",
                                        "email": "test@example.com"
                                    },
                                    "car": {
                                        "id": 1,
                                        "model": {
                                            "id": 1,
                                            "name": "Model 3",
                                            "brand": {
                                                "id": 1,
                                                "name": "Tesla"
                                            }
                                        }
                                    },
                                    "start_date": "2024-01-01",
                                    "month": 12,
                                    "end_date": "2024-12-31",
                                    "billing_key": "billing_key_123"
                                },
                                "start_date": "2024-01-01",
                                "end_date": "2024-12-31",
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z",
                                "is_active": True
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="인증이 필요합니다.",
                    errors={"detail": "Authentication credentials were not provided."}
                )
            ]
        }


# Review Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class ReviewSchema:
    @staticmethod
    def get_review_list():
        return {
            'summary': "리뷰 목록 조회",
            'description': "모든 리뷰 목록을 조회합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="리뷰 목록 조회 성공",
                    data={
                        "reviews": [
                            {
                                "id": 1,
                                "model": {
                                    "id": 1,
                                    "name": "Model 3",
                                    "brand": {
                                        "id": 1,
                                        "name": "Tesla"
                                    }
                                },
                                "user": {
                                    "id": 1,
                                    "username": "testuser",
                                    "email": "test@example.com"
                                },
                                "content": "정말 좋은 차입니다!",
                                "image": "https://example.com/review1.jpg",
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z",
                                "is_verified": True,
                                "is_active": True
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="리뷰 목록을 불러오는 중 오류가 발생했습니다.",
                    errors={"detail": "Database connection error"}
                )
            ]
        }
    
    @staticmethod
    def get_model_reviews():
        return {
            'summary': "모델별 리뷰 목록 조회",
            'description': "특정 모델의 리뷰 목록을 조회합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="리뷰 목록 조회 성공",
                    data={
                        "reviews": [
                            {
                                "id": 1,
                                "model": 1,
                                "user": {
                                    "id": 1,
                                    "username": "testuser",
                                    "email": "test@example.com"
                                },
                                "content": "정말 좋은 차입니다!",
                                "image": "https://example.com/review1.jpg",
                                "created_at": "2024-01-01T00:00:00Z",
                                "modified_at": "2024-01-01T00:00:00Z",
                                "is_verified": True,
                                "is_active": True
                            }
                        ]
                    }
                ),
                CommonExamples.error_example(
                    message="리뷰 목록을 불러오는 중 오류가 발생했습니다.",
                    errors={"detail": "Database connection error"}
                )
            ]
        }
    
    @staticmethod
    def create_review():
        return {
            'summary': "리뷰 작성",
            'description': "특정 모델에 대한 리뷰를 작성합니다. 구독자만 작성 가능합니다.",
            'request': ReviewCreateSerializer,
            'responses': {
                201: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="리뷰 추가 성공",
                    data={
                        "review": {
                            "id": 1,
                            "model": 1,
                            "user": 1,
                            "content": "정말 좋은 차입니다!",
                            "image": "https://example.com/review1.jpg",
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z",
                            "is_verified": False,
                            "is_active": True
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="입력 정보가 올바르지 않습니다.",
                    errors={"content": ["This field is required."]}
                )
            ]
        }
    
    @staticmethod
    def get_review_detail():
        return {
            'summary': "리뷰 상세 조회",
            'description': "특정 리뷰의 상세 정보를 조회합니다.",
            'operation_id': 'subscriptions_reviews_detail',
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="리뷰 상세 조회 성공",
                    data={
                        "review": {
                            "id": 1,
                            "model": {
                                "id": 1,
                                "name": "Model 3",
                                "brand": {
                                    "id": 1,
                                    "name": "Tesla"
                                }
                            },
                            "user": {
                                "id": 1,
                                "username": "testuser",
                                "email": "test@example.com"
                            },
                            "content": "정말 좋은 차입니다!",
                            "image": "https://example.com/review1.jpg",
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-01T00:00:00Z",
                            "is_verified": True,
                            "is_active": True,
                            "likes_count": 5,
                            "is_liked": False
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="요청하신 리뷰를 찾을 수 없습니다.",
                    errors={"detail": "Review not found"}
                )
            ]
        }
    
    @staticmethod
    def update_review():
        return {
            'summary': "리뷰 수정",
            'description': "리뷰를 수정합니다. 작성자만 수정 가능합니다.",
            'request': ReviewCreateSerializer,
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="리뷰 수정 성공",
                    data={
                        "review": {
                            "id": 1,
                            "model": 1,
                            "user": 1,
                            "content": "수정된 리뷰 내용입니다.",
                            "image": "https://example.com/review1_updated.jpg",
                            "created_at": "2024-01-01T00:00:00Z",
                            "modified_at": "2024-01-02T00:00:00Z",
                            "is_verified": True,
                            "is_active": True
                        }
                    }
                ),
                CommonExamples.error_example(
                    message="입력 정보가 올바르지 않습니다.",
                    errors={"content": ["This field is required."]}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "You do not have permission to perform this action."}
                )
            ]
        }
    
    @staticmethod
    def delete_review():
        return {
            'summary': "리뷰 삭제",
            'description': "리뷰를 삭제합니다. 작성자만 삭제 가능합니다.",
            'responses': {
                204: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="리뷰 삭제 성공",
                    data={}
                ),
                CommonExamples.error_example(
                    message="요청하신 리뷰를 찾을 수 없습니다.",
                    errors={"detail": "Review not found"}
                ),
                CommonExamples.error_example(
                    message="권한이 없습니다.",
                    errors={"detail": "You do not have permission to perform this action."}
                )
            ]
        }

    @staticmethod
    def get_review_like_status():
        return {
            'summary': "리뷰 좋아요 여부 조회",
            'description': "특정 리뷰에 대한 사용자의 좋아요 여부를 조회합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="리뷰 좋아요 여부 조회 성공",
                    data={
                        "liked": True
                    }
                ),
                CommonExamples.error_example(
                    message="요청하신 리뷰를 찾을 수 없습니다.",
                    errors={"detail": "Review not found"}
                )
            ]
        }
    
    @staticmethod
    def add_review_like():
        return {
            'summary': "리뷰 좋아요 추가",
            'description': "특정 리뷰에 좋아요를 추가합니다.",
            'request': None,
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="리뷰 좋아요 추가 성공",
                    data={
                        "message": "liked"
                    }
                ),
                CommonExamples.error_example(
                    message="요청하신 리뷰를 찾을 수 없습니다.",
                    errors={"detail": "Review not found"}
                )
            ]
        }
    
    @staticmethod
    def remove_review_like():
        return {
            'summary': "리뷰 좋아요 취소",
            'description': "특정 리뷰의 좋아요를 취소합니다.",
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="리뷰 좋아요 취소 성공",
                    data={
                        "message": "UnLiked"
                    }
                ),
                CommonExamples.error_example(
                    message="요청하신 리뷰를 찾을 수 없습니다.",
                    errors={"detail": "Review not found"}
                )
            ]
        }