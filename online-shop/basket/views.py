from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from basket.models import BasketItem, Basket
from basket.serializers import BasketItemSerializer
from product.models import Product


class BasketItemAPIView(APIView):
    def get(self, request):
        try:
            qs = BasketItem.objects.filter(basket__user=request.user)
            if not qs.exists():
                return Response(
                    {"message": "No basket items found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = BasketItemSerializer(qs, many=True)
            return Response(serializer.data)
        except Exception as exp:
            return Response(
                {"error": f"Failed to retrieve basket items: {exp}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        _id = request.data.get("id")
        count = request.data.get("count")
        if not _id or not count:
            return Response(
                {"error": "Product ID and count are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            count = int(count)
            if count <= 0:
                return Response(
                    {"error": "Count must be a positive integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError:
            return Response(
                {"error": "Count must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.get(id=_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )

        basket, created = Basket.objects.get_or_create(user=request.user)

        basket_item, created = BasketItem.objects.get_or_create(
            basket=basket, product=product
        )
        basket_item.amount += count
        basket_item.save()

        basket_items = BasketItem.objects.filter(basket=basket)
        serializer = BasketItemSerializer(basket_items, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
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
