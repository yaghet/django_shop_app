from decimal import Decimal

from django.conf import settings

from product.models import Product
from product.serializers import ProductSerializer


class SessionCart(object):

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart


    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'amount': 0,
                                     'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['amount'] = quantity
        else:
            self.cart[product_id]['amount'] += quantity
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product, count):
        product_id = str(product)

        if product_id in self.cart:
            self.cart[product_id]['amount'] -= count
            if self.cart[product_id]['amount'] == 0:
                del self.cart[product_id]

            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        product_map = {product.id: product for product in products}

        for product_id_str, item in self.cart.items():
            product_id = int(product_id_str)
            product = product_map.get(product_id)
            if not product:
                continue

            product_data = ProductSerializer(product).data

            product_data['count'] = item['amount']
            product_data['price'] = float(item['price'])  # чтобы был float, как на фронте
            product_data['reviews'] = len(product_data.get('reviews', []))
            yield product_data

    def __len__(self):
        return sum(item['amount'] for item in self.cart.values())

    def get_total_price(self):
        total = Decimal('0.0')
        for item in self.cart.values():
            total += Decimal(item['price']) * int(item['amount'])
        return total

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True