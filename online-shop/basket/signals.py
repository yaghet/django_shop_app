from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from basket.models import Basket, BasketItem
from basket.session_cart import SessionCart
from product.models import Product


@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    session_cart = SessionCart(request)
    basket, _ = Basket.objects.get_or_create(user=user)

    try:
        for product_id_str, item in session_cart.cart.items():
            product_id = int(product_id_str)
            product = Product.objects.get(id=product_id)
            basket_item, created = BasketItem.objects.get_or_create(basket=basket, product=product)
            basket_item.amount += item['amount']
            basket_item.save()

        session_cart.clear()
    except AttributeError:
        print('Not logged in')
        pass
    except Product.DoesNotExist:
        pass
