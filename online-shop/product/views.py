from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from product.models import Product
from product.serializers import ProductSerializer, ReviewSerializer


class ProductDetailView(APIView):
    """
    APIView для получения детальной информации о продукте по его ID.

    Методы:
        get(request, id): Возвращает данные продукта с указанным ID.
    """

    @extend_schema(
        tags=['Product'],
        responses=ProductSerializer,
        description="Получить детальную информацию о продукте по ID."
    )
    def get(self, request, id):
        """
        Обрабатывает GET-запрос для получения информации о продукте.

        Args:
            request (Request): Объект запроса.
            id (int): Идентификатор продукта.

        Returns:
            Response: JSON с данными продукта и статусом 200,
                      или 404, если продукт не найден.
        """

        product = get_object_or_404(Product, id=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


class ProductReviewView(APIView):
    """
    APIView для создания нового отзыва о продукте, по его id.
    Методы:
        post(request, id): Создает новый отзыв для продукта с указанным ID.
    """

    @extend_schema(
        tags=['Product'],
        request=ReviewSerializer,
        responses={
            201: ReviewSerializer(many=True),
            400: OpenApiResponse(description="Ошибка валидации данных"),
            500: OpenApiResponse(description="Внутренняя ошибка сервера"),
        },
        description="Создать новый отзыв для продукта по ID."
    )
    def post(self, request, id):
        """
        Обрабатывает POST-запрос для создания отзыва.

        Args:
            request (Request): Объект запроса с данными отзыва.
            id (int): Идентификатор продукта, к которому добавляется отзыв.

        Returns:
            Response:
                - При успешном создании отзыва возвращает список всех отзывов продукта и статус 201.
                - При ошибках валидации возвращает ошибки и статус 400.
                - При внутренних ошибках сервера возвращает сообщение об ошибке и статус 500.
        """

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
