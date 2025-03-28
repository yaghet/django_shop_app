from django.db import models
from django.contrib.auth.models import User

from product.models import Product


class Basket(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.amount == 0:
            self.delete()
        else:
            super().save(*args, **kwargs)