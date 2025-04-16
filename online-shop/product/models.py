from django.core.validators import MaxValueValidator
from django.db import models

from catalog.models import Category, SubCategory
from tags.models import Tag


def upload_product_preview(instance, filename):
    return f"products/product_{instance.pk}/preview/{filename}"


class ProductImages(models.Model):
    class Meta:
        verbose_name = "ProductImages"

    src = models.ImageField(upload_to=upload_product_preview, verbose_name="Link")
    alt = models.CharField(
        max_length=12, default="product_preview", verbose_name="Alt product image"
    )

    def __str__(self):
        return self.src.name


class Review(models.Model):
    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    author = models.CharField(max_length=100, verbose_name="Автор")
    email = models.EmailField(null=True, blank=True)
    text = models.TextField(max_length=250)
    rate = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(5)]
    )
    date = models.DateTimeField(auto_now_add=True)


class Product(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=50)
    fullDescription = models.TextField(max_length=250)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    count = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    freeDelivery = models.BooleanField(default=False)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    specifications = models.ManyToManyField("Specification", blank=True)
    images = models.ManyToManyField(ProductImages, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    reviews = models.ManyToManyField(Review, blank=True)

    rating = models.DecimalField(
        decimal_places=1,
        max_digits=2,
        default=0,
    )

    is_limited = models.BooleanField(default=False)
    is_banner = models.BooleanField(default=False)

    def get_average_rating(self):
        reviews = Review.objects.filter(product=self).values_list("rate", flat=True)
        if reviews:
            return sum(reviews) / len(reviews)
        else:
            return 0

    def __str__(self):
        return self.title


class Specification(models.Model):
    class Meta:
        verbose_name = "Specification"
        verbose_name_plural = "Specifications"

    name = models.CharField(max_length=30)
    value = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class SalePrice(models.Model):
    class Meta:
        verbose_name = "SalePrice"
        verbose_name_plural = "SalePrices"

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    salePrice = models.DecimalField(decimal_places=2, max_digits=8)
    dateFrom = models.DateField()
    dateTo = models.DateField()
