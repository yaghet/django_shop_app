from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from basket.models import BasketItem, Basket
from basket.serializers import BasketItemSerializer
from product.models import Product
from product.serializers import ProductSerializer

from decimal import Decimal
from django.conf import settings
from product.models import Product


class BasketItemAPIView(APIView):

    @extend_schema(
        tags=['Basket'],
        request=BasketItemSerializer(many=True),
        description="Получение всех товаров в корзине текущего пользователя",
        responses={
            200: BasketItemSerializer(many=True),
            401: OpenApiResponse(description="Пользователь не аутентифицирован"),
            404: OpenApiResponse(description="Товары в корзине не найдены"),
        },
    )
    def get(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        qs = BasketItem.objects.filter(basket__user=request.user)
        if not qs.exists():
            return Response({"message": "No basket items found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BasketItemSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=BasketItemSerializer,
        responses=BasketItemSerializer(many=True),
        tags=['Basket'],
        description="Добавление товара в корзину или увеличение количества"
    )
    def post(self, request):
        _id = request.data.get("id")
        count = request.data.get("count")

        if not _id or not count:
            return Response({"error": "Product ID and count are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            count = int(count)
            if count <= 0:
                return Response({"error": "Count must be a positive integer"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Count must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        basket, _ = Basket.objects.get_or_create(user=request.user)
        basket_item, created = BasketItem.objects.get_or_create(basket=basket, product=product)
        basket_item.amount += count
        basket_item.save()

        basket_items = BasketItem.objects.filter(basket=basket)
        serializer = BasketItemSerializer(basket_items, many=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @extend_schema(
        tags=['Basket'],
        request={
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "ID продукта"},
                "count": {"type": "integer", "description": "Количество для удаления"},
            },
            "required": ["id", "count"],
        },
        responses={
            200: BasketItemSerializer(many=True),
            400: OpenApiResponse(description="Ошибка валидации данных"),
            404: OpenApiResponse(description="Корзина или товар не найдены"),
            500: OpenApiResponse(description="Внутренняя ошибка сервера"),
        },
        description="Удаление или уменьшение количества товара в корзине",
    )
    def delete(self, request):
        _id = request.data.get("id")
        count = request.data.get("count")

        if not _id:
            return Response(
                {"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            basket = Basket.objects.get(user=request.user)
            basket_item = BasketItem.objects.get(basket=basket, product_id=_id)

            if basket_item.amount - count == 0:
                basket_item.delete()
            else:
                basket_item.amount -= count
                basket_item.save()

            basket_items = BasketItem.objects.filter(basket=basket)
            serializer = BasketItemSerializer(basket_items, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Basket.DoesNotExist:
            return Response(
                {"error": "Basket not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except BasketItem.DoesNotExist:
            return Response(
                {"error": "Product not found in the basket"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as exp:
            return Response(
                {"error": f"Failed to delete basket item: {exp}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
