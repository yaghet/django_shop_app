from django.db.models import Count, Q
from rest_framework import status, serializers
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer

from catalog.models import Category
from catalog.serializers import CategorySerializer
from product.models import Product, SalePrice
from product.serializers import ProductSerializer, SalesProductSerializer


class SalesView(GenericAPIView):

    @extend_schema(
        tags=['Catalog'],
        responses=inline_serializer(
            name='SalesResponse',
            fields={
                'items': SalesProductSerializer(many=True),
                'currentPage': serializers.IntegerField(),
                'lastPage': serializers.IntegerField(),
            }
        ),
        description="Получение списка товаров со скидками"
    )
    def get(self, request) -> Response:
        sales = SalePrice.objects.all()
        serializer = SalesProductSerializer(
            sales,
            many=True,
        )
        data = {
            "items": serializer.data,
            "currentPage": int(request.GET.get("currentPage")),
            "lastPage": 2,
        }
        return Response(data, status=status.HTTP_200_OK)


class CategoryListView(GenericAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    @extend_schema(
        tags=['Catalog'],
        responses=CategorySerializer(many=True),
        description="Получение всех категорий продуктов",
    )
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CatalogListAPIView(APIView):

    @extend_schema(
        tags=['Catalog'],
        responses=inline_serializer(
            name='CatalogResponse',
            fields={
                'items': ProductSerializer(many=True),
                'currentPage': serializers.IntegerField(),
                'lastPage': serializers.IntegerField(),
            }
        ),
        description="Получение списка продуктов с фильтрацией и сортировкой"
    )
    def get(self, request) -> Response:
        name = request.query_params.get("filter[name]") or None
        if request.query_params.get("filter[available]") == "true":
            archived = False
        else:
            archived = True
        if request.query_params.get("filter[freeDelivery]") == "true":
            freeDelivery = True
        else:
            freeDelivery = False
        tags = request.query_params.getlist("tags[]") or None

        minPrice = request.query_params.get("filter[minPrice]")
        maxPrice = request.query_params.get("filter[maxPrice]")
        category = request.META["HTTP_REFERER"].split("/")[4] or None
        sort = request.GET.get("sort")
        if request.GET.get("sortType") == "inc":
            sortType = "-"
        else:
            sortType = ""
        products_list = Product.objects.filter(
            price__range=(minPrice, maxPrice),
            count__gt=0,
        )
        if category:
            if category.startswith("?filter="):
                if name is None:
                    name = category[8:]
            else:
                products_list = products_list.filter(Q(category_id__in=category))

        if name:
            products_list = products_list.filter(
                title__iregex=name,
            )
        if tags:
            products_list = products_list.filter(
                tags__in=tags,
            )
        if freeDelivery:
            products_list = products_list.filter(
                freeDelivery=freeDelivery,
            )
        if archived:
            products_list = products_list.filter(
                count__gte=1,
            )
        if sort == "reviews":
            products_list = products_list.annotate(
                count_reviews=Count("reviews"),
            ).order_by(f"{sortType}count_reviews")
        else:
            products_list = products_list.order_by(
                f"{sortType}{sort}",
            )
        products_list = products_list.prefetch_related(
            "images",
            "tags",
        )
        serialized = ProductSerializer(
            products_list,
            many=True,
        )
        currentPage = int(request.GET.get("currentPage"))
        data = {"items": serialized.data, "currentPage": currentPage, "lastPage": 2}
        return Response(data, status=status.HTTP_200_OK)


class LimitedProductsView(GenericAPIView):

    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    @extend_schema(
        tags=['Catalog'],
        responses=ProductSerializer(many=True),
        description="Получение списка ограниченных продуктов (лимитированных)"
    )
    def get(self, request) -> Response:
        products = Product.objects.filter(is_limited=True)[:8]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PopularProductsView(GenericAPIView):

    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    @extend_schema(
        tags=['Catalog'],
        responses=ProductSerializer(many=True),
        description="Получение списка популярных продуктов по рейтингу"
    )
    def get(self, request) -> Response:
        products = Product.objects.order_by("rating")[:10]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BannerListView(ListAPIView):
    serializer_class = ProductSerializer

    @extend_schema(
        tags=['Catalog'],
        responses=ProductSerializer(many=True),
        description="Получение списка продуктов для баннера"
    )
    def get_queryset(self):
        return Product.objects.filter(is_banner=True)[:3]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
