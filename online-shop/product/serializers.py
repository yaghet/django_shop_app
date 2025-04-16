from django.conf import settings
from rest_framework import serializers

from catalog.serializers import CategorySerializer
from product.models import Product, ProductImages, Review, SalePrice, Specification
from tags.serializers import TagSerializer


class ImagesWithDefaultMixin:
    DEFAULT_IMAGE_URL = "default_image/not_yet.jpeg"
    DEFAULT_IMAGE_ALT = "Изображение по умолчанию"

    def get_images_with_default(self, images_queryset):
        if images_queryset.exists():
            return [
                {"src": settings.MEDIA_URL + image.src.name, "alt": image.alt}
                for image in images_queryset
            ]
        else:
            return [
                {
                    "src": settings.MEDIA_URL + self.DEFAULT_IMAGE_URL,
                    "alt": self.DEFAULT_IMAGE_ALT,
                }
            ]


class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ["src", "alt"]


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ["id", "name", "value"]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class ProductSerializer(ImagesWithDefaultMixin, serializers.ModelSerializer):
    category = CategorySerializer()
    tags = TagSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    specifications = SpecificationSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "fullDescription",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "specifications",
            "rating",
        ]

    def get_images(self, obj):
        return self.get_images_with_default(obj.images.all())


class SalesProductSerializer(ImagesWithDefaultMixin, serializers.ModelSerializer):
    class Meta:
        model = SalePrice
        fields = ["id", "price", "salePrice", "dateFrom", "dateTo", "title", "images"]

    price = serializers.FloatField(source="product.price")
    title = serializers.CharField(source="product.title")
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        return self.get_images_with_default(obj.product.images.all())
