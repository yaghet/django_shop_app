from datetime import datetime

from django.db import transaction

from basket.models import Basket, BasketItem
from order.models import Order, Payment


class PaymentService:
    @staticmethod
    def process_payment(user, order_id, card_number, month, year):
        valid_period = f"{month}/{year}"

        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return {"error": "Order not found"}, 404

        try:
            basket = Basket.objects.get(user=user)
        except Basket.DoesNotExist:
            return {"error": "Basket not found"}, 404

        basket_items = BasketItem.objects.filter(basket=basket)

        for item in basket_items:
            if item.product.count < item.amount:
                return {
                    "Error": f"Not enough items for product {item.product.title}"
                }, 400

        with transaction.atomic():
            payment = Payment.objects.create(
                order=order, card_number=card_number, valid_period=valid_period
            )

            for item in basket_items:
                product = item.product
                product.count -= item.amount
                product.save()

            order.status = "Paid"
            order.save()

            payment.success = True
            payment.save()

            basket_items.delete()

        return {"success": True}, 200


def check_year_and_month(year, month):
    if month < 1 or month > 12:
        return False

    cur_year = datetime.now().year % 25
    cur_month = datetime.now().month

    if not all([cur_month < month, cur_year < year]):
        return False

    return True


def check_card_number(card_number):
    if not 12 <= len(card_number) <= 16:
        return False
    return True
