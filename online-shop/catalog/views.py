from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from catalog.models import Category
from catalog.serializers import CategorySerializer
from product.models import Product
from product.serializers import ProductSerializer


class CategoryListView(GenericAPIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CatalogListAPIView(GenericAPIView):
    def get(self, request) -> Response:
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        data = {
            "items": serializer.data,
            "currentPage": 1,
            "lastPage": 3,
        }
        return Response(data)
