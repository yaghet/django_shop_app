from django.core.validators import MinValueValidator
from django.db import models


def upload_image_of_product(instance: "Product", filename: str) -> str:
    """
    :param instance:
    :param filename:
    :return: str

    Функция генерации путей для сохранения изображений продукта

    """
    return 'products/product_{id}/preview/{filename}'.format(id=instance.pk, filename=filename)


class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    short_description = models.TextField(max_length=500, blank=True)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_image_of_product)