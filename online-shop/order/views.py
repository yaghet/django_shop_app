from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from order.models import Order, OrderProduct
from order.serializers import OrderSerializer
from order.services import PaymentService, check_card_number, check_year_and_month
from product.models import Product


class OrdersCreateView(APIView):

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

    def get(self, request: Request):
        orders = Order.objects.filter(user_id=request.user.profile.pk)
        serialized = OrderSerializer(orders, many=True)
        return Response(serialized.data)


class OrderDetailView(APIView):
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
