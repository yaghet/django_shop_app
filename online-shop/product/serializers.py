from rest_framework import serializers
from django.conf import settings
from catalog.serializers import CategorySerializer
from product.models import Product, Specification, Review, ProductImages
from tags.serializers import TagSerializer


class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ['src', 'alt']


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['id', 'name', 'value']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    tags = TagSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True)
    specifications = SpecificationSerializer(many=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'price',
            'count',
            'date',
            'title',
            'description',
            'fullDescription',
            'freeDelivery',
            'images',
            'tags',
            'reviews',
            'specifications',
            'rating',
        ]

    def get_images(self, obj):
        if obj.images.exists():
            return [
                {"src": settings.MEDIA_URL + image.src.name, "alt": image.alt} for image in obj.images.all()
            ]
        else:
            default_image_url = 'default_image/not_yet.jpeg'
            return [{"src": settings.MEDIA_URL + default_image_url, "alt": "Изображение по умолчанию"}]
