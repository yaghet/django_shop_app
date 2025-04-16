from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from product.models import Product
from product.serializers import ProductSerializer, ReviewSerializer


class ProductDetailView(APIView):
    def get(self, request, id):
        product = get_object_or_404(Product, id=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


class ProductReviewView(APIView):
    def post(self, request, id):
        product = get_object_or_404(Product, id=id)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            try:
                review = serializer.save()
                product.reviews.add(review)
                reviews = product.reviews.all().values()
                return Response(list(reviews), status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
