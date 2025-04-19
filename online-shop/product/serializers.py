from django.conf import settings
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from catalog.serializers import CategorySerializer
from product.models import Product, ProductImages, Review, SalePrice, Specification
from tags.serializers import TagSerializer


class ImagesWithDefaultMixin:
    """
    Миксин для сериализаторов, предоставляющий метод для получения списка изображений.
    Если изображения отсутствуют, возвращает изображение по умолчанию.

    Атрибуты:
        DEFAULT_IMAGE_URL (str): Путь к изображению по умолчанию.
        DEFAULT_IMAGE_ALT (str): Альтернативный текст для изображения по умолчанию.
    """

    DEFAULT_IMAGE_URL = "default_image/not_yet.jpeg"
    DEFAULT_IMAGE_ALT = "Изображение по умолчанию"

    def get_images_with_default(self, images_queryset):
        """
        Возвращает список словарей с данными изображений из queryset.
        Если queryset пуст, возвращает список с одним изображением по умолчанию
        """
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
    """
    Сериализатор для модели ProductImages.

    Поля:
        src (ImageField): Путь к изображению.
        alt (str): Альтернативный текст изображения.
    """
    class Meta:
        model = ProductImages
        fields = ["src", "alt"]


class SpecificationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Specification.

    Поля:
        id (int): Идентификатор спецификации.
        name (str): Название спецификации.
        value (str): Значение спецификации.
    """
    class Meta:
        model = Specification
        fields = ["id", "name", "value"]


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review.

    Поля:
        Все поля модели Review.
    """
    class Meta:
        model = Review
        fields = "__all__"


class ProductSerializer(ImagesWithDefaultMixin, serializers.ModelSerializer):
    """
    Сериализатор для модели Product с вложенными сериализаторами для тегов, отзывов,
    спецификаций и изображений.

    Поля:
        id (int): Идентификатор продукта.
        category (Category): Категория продукта.
        price (float): Цена продукта.
        count (int): Количество на складе.
        date (datetime): Дата создания/обновления.
        title (str): Название продукта.
        description (str): Краткое описание.
        fullDescription (str): Полное описание.
        freeDelivery (bool): Бесплатная доставка.
        images (list): Список изображений с обработкой по умолчанию.
        tags (list): Список тегов.
        reviews (list): Список отзывов.
        specifications (list): Список спецификаций.
        rating (float): Рейтинг продукта.
    """

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

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_images(self, obj: Product) -> list[dict]:
        """
        Получает список изображений продукта с использованием миксина.

        Args:
            obj (Product): Экземпляр продукта.

        Returns:
            list[dict]: Список изображений с ключами 'src' и 'alt'.
        """
        return self.get_images_with_default(obj.images.all())


class SalesProductSerializer(ImagesWithDefaultMixin, serializers.ModelSerializer):
    """
    Сериализатор для модели SalePrice с дополнительными полями из связанного продукта.

    Поля:
        id (int): Идентификатор акции.
        price (float): Цена продукта.
        salePrice (float): Цена со скидкой.
        dateFrom (datetime): Дата начала акции.
        dateTo (datetime): Дата окончания акции.
        title (str): Название продукта (из связанной модели Product).
        images (list): Список изображений продукта с обработкой по умолчанию.
    """
    class Meta:
        model = SalePrice
        fields = ["id", "price", "salePrice", "dateFrom", "dateTo", "title", "images"]

    price = serializers.FloatField(source="product.price")
    title = serializers.CharField(source="product.title")
    images = serializers.SerializerMethodField()

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_images(self, obj: Product) -> list[dict]:
        """
        Получает список изображений продукта со скидкой с использованием миксина.

        Args:
            obj (Product): Экземпляр продукта со скидкой.

        Returns:
            list[dict]: Список изображений с ключами 'src' и 'alt'.
        """
        return self.get_images_with_default(obj.product.images.all())
