from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CatalogListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['category', 'tags', 'freeDelivery']
    search_fields = ['title']
    ordering_fields = ['price', 'rating', 'count_reviews']
    ordering = ['price']

    def get_queryset(self):
        queryset = Product.objects.filter(count__gt=0).prefetch_related('images', 'tags')
        min_price = self.request.query_params.get('filter[minPrice]')
        max_price = self.request.query_params.get('filter[maxPrice]')
        if min_price and max_price:
            queryset = queryset.filter(price__range=(min_price, max_price))
        return queryset