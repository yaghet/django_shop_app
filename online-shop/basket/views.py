import json

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from basket.models import BasketItem, Basket
from basket.session_cart import SessionCart
from basket.serializers import BasketItemSerializer

from product.models import Product


class BasketItemAPIView(APIView):

    permission_classes = (AllowAny,)

    def get_id_and_count(self, request):

        """ Функция парсит Json структуру данных для метода DELETE (возвращает id товара и количество) """

        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            id = data.get('id')
            count = data.get('count')
            return id, count

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return None, None

    def get(self, request):

        if request.user.is_authenticated:
            basket = Basket.objects.filter(user=request.user)
            qs = BasketItem.objects.filter(basket__in=basket)
            serializer = BasketItemSerializer(qs, many=True)
            return Response(serializer.data)

        else:
            basket = SessionCart(request)
            products_data = []

            for product_data in basket:
                products_data.append(product_data)

            return Response(products_data)

    def post(self, request):

        _id = request.data.get('id')
        count = request.data.get('count')

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

        if request.user.is_authenticated:
            basket, _ = Basket.objects.get_or_create(user=request.user)
            basket_item, _ = BasketItem.objects.get_or_create(basket=basket, product=product)
            basket_item.amount += count
            basket_item.save()

            basket_items = BasketItem.objects.filter(basket=basket)
            serializer = BasketItemSerializer(basket_items, many=True)

            return Response(serializer.data)

        else:
            basket = SessionCart(request)
            basket.add(product, count)
            products_data = list(basket)
            return Response(products_data)

    def delete(self, request):
        _id, count = self.get_id_and_count(request)

        if not _id:
            return Response(
                {"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.is_authenticated:
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
        else:
            basket = SessionCart(request)
            basket.remove(_id, count)
            products_data = list(basket)
            return Response(products_data)
