from profile.models import Profile

from django.db import models

from product.models import Product


class Order(models.Model):
    """ Модель заказа продуктов. """

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    deliveryType = models.CharField(max_length=30, default="free")
    paymentType = models.CharField(max_length=30, default="online")
    totalCost = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    status = models.CharField(max_length=30, default="accepted")
    city = models.CharField(max_length=100)
    address = models.TextField(max_length=256)
    products = models.ManyToManyField(Product, related_name="orders")

    def get_full_name(self):
        return self.user.fullName


class OrderProduct(models.Model):
    """ Модель для связи между заказом и товаром с указанием количества """

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    count = models.PositiveIntegerField(default=1)


class Payment(models.Model):
    """
    Модель оплаты заказа.

    Атрибуты:
    - order: заказ, к которому относится оплата.
    - card_number: номер карты оплаты.
    - valid_period: срок действия карты.
    - success: статус успешности оплаты.

    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    valid_period = models.CharField(max_length=15)
    success = models.BooleanField(default=False)
