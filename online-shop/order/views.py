from rest_framework import status, serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer

from order.models import Order, OrderProduct
from order.serializers import OrderSerializer
from order.services import PaymentService, check_card_number, check_year_and_month
from product.models import Product


class OrdersCreateView(APIView):
    """
    APIView для создания и отображения заказов текущего пользователя.

    Методы:
        get(request, id): Возвращает данные заказа с помощью получения профиля пользователя по его id.
        post(request): Создание нового заказа с выбранными пользователем продуктами из корзины.
    """
    @extend_schema(
        tags=['Orders'],
        responses=OrderSerializer(many=True),
        description="Получение списка заказов текущего пользователя"
    )
    def get(self, request: Request):
        orders = Order.objects.filter(user_id=request.user.profile.pk)
        serialized = OrderSerializer(orders, many=True)
        return Response(serialized.data)

    @extend_schema(
        tags=['Orders'],
        request=inline_serializer(
            name='OrderCreateRequest',
            many=True,
            fields={
                'id': serializers.IntegerField(),
                'count': serializers.IntegerField(),
                'price': serializers.FloatField(),
            }
        ),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "orderId": {"type": "integer", "description": "ID созданного заказа"},
                },
            },
            400: OpenApiResponse(description="Ошибка в данных запроса"),
        },
        description="Создание нового заказа с продуктами"
    )
    def post(self, request: Request, *args, **kwargs):
        products_in_order = [
            (obj["id"], obj["count"], obj["price"]) for obj in request.data
        ]

        products = Product.objects.filter(
            id__in=[obj[0] for obj in products_in_order],
        )

        total_cost = sum(float(obj[2]) * int(obj[1]) for obj in products_in_order)

        order = Order.objects.create(
            user=request.user.profile,
            totalCost=total_cost,
        )

        order.products.set(products)
        order.save()

        data = {
            "orderId": order.pk,
        }
        return Response(data)


class OrderDetailView(APIView):
    """
    APIView для получения детальной информации о конкретном заказае по его id

    Методы:
        - get(request, id): Отображение информации о заказе по его id
        - post(request, id): Обновление данных о заказа по его id
    """
    @extend_schema(
        tags=['Orders'],
        responses=OrderSerializer,
        description="Получение детальной информации о заказе по ID"
    )
    def get(self, request, id):
        order = Order.objects.get(pk=id)
        serialized = OrderSerializer(order)
        data = serialized.data

        products_in_order = data["products"]
        query = OrderProduct.objects.filter(
            order_id=id,
        )
        product_counts = {obj.product.pk: obj.count for obj in query}
        for product in products_in_order:
            product["count"] = product_counts.get(product["id"], 0)

        return Response(data)

    @extend_schema(
        tags=['Orders'],
        request=inline_serializer(
            name='OrderUpdateRequest',
            fields={
                'deliveryType': serializers.CharField(),
                'city': serializers.CharField(),
                'address': serializers.CharField(),
                'paymentType': serializers.CharField(),
                'products': serializers.ListField(
                    child=serializers.DictField()
                ),
            }
        ),
        responses={
            201: OpenApiResponse(
                response={"type": "object", "properties": {}},
                description="Заказ успешно обновлен"
            ),
            400: OpenApiResponse(description="Ошибка в данных запроса"),
            404: OpenApiResponse(description="Заказ не найден"),
        },
        description="Обновление информации о заказе"
    )
    def post(self, request: Request, id):
        order = Order.objects.get(pk=id)

        data = request.data
        order.delivery_type = data["deliveryType"]
        order.city = data["city"]
        order.address = data["address"]
        order.payment_type = data["paymentType"]
        order.status = "awaiting payment"

        if data["deliveryType"] == "express":
            order.totalCost += 500
        else:
            if order.totalCost < 1500:
                order.totalCost += 500

        for product in data["products"]:
            OrderProduct.objects.get_or_create(
                order_id=order.pk,
                product_id=product["id"],
                defaults={"count": product["count"]},
            )

        order.save()
        return Response(request.data, status=status.HTTP_201_CREATED)


class PaymentView(APIView):

    @extend_schema(tags=['Payment'],
                   request=inline_serializer(
                       name='PaymentRequest',
                       fields={
                           'number': serializers.CharField(
                               max_length=19,
                               help_text='Номер банковской карты'
                           ),
                           'month': serializers.IntegerField(
                               min_value=1,
                               max_value=12,
                               help_text='Месяц окончания срока действия карты'
                           ),
                           'year': serializers.IntegerField(
                               min_value=2000,
                               max_value=2100,
                               help_text='Год окончания срока действия карты'
                           ),
                       }
                   ),
                   responses={
                       200: OpenApiResponse(
                           response=inline_serializer(
                               name='PaymentSuccessResponse',
                               fields={'message': serializers.CharField(default='Платеж успешно обработан')}
                           ),
                           description='Платеж успешно обработан'
                       ),
                       400: OpenApiResponse(
                           response=inline_serializer(
                               name='PaymentErrorResponse',
                               fields={'error': serializers.CharField(default='Ошибка валидации платежных данных')}
                           ),
                           description='Ошибка валидации платежных данных'
                       ),
                       402: OpenApiResponse(
                           response=inline_serializer(
                               name='PaymentDeclinedResponse',
                               fields={'error': serializers.CharField(default='Платеж отклонён')}
                           ),
                           description='Платеж отклонён'
                       ),
                   },
                   description='Обработка платежа по заказу'
                   )
    def post(self, request, id):
        data = request.data

        card = data.get("number")
        month = data.get("month")
        year = data.get("year")

        if not all([card, month, year]):
            return Response(
                {"error": "Missing payment information"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not check_card_number(card):
            return Response(
                {"error": "Invalid card number"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not check_year_and_month(int(year), int(month)):
            return Response(
                {"error": "Invalid year and month"}, status=status.HTTP_400_BAD_REQUEST
            )

        result, code = PaymentService.process_payment(
            request.user, id, card, month, year
        )
        return Response(result, status=code)
