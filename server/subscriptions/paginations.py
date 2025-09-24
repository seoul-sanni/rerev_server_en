# subscriptions/paginations.py
app_name = 'subscriptions'

from rest_framework.pagination import PageNumberPagination

class SubscriptionPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100