from django.db import models


def upload_image_category_path(instance: 'Category', filename: str) -> str:
    """
    Функция формирует путь для сохранения изображения для Модели Category

    """
    return f"categories/category_{instance.title}/preview/{filename}"


def upload_image_subcategory_path(instance: 'SubCategory', filename: str) -> str:
    """
    Функция формирует путь для сохранения изображения для Модели SubCategory

    """
    return f"subcategories/category_{instance.pk}/preview/{filename}"


class Category(models.Model):
    """
    Модель категории товара.

    Атрибуты:
    - title: имя категории.
    - image: изображение категории.
    """

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    title = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to=upload_image_category_path, null=True, blank=True
    )

    def __str__(self):
        return self.title


class SubCategory(models.Model):
    """
    Модель подкатегории товара, имеет связь многие ко одной по отношению к модели Category

    Атрибуты:
    - title: Название категории.
    - image: изображение подкатегории.
    - category: связь с моделью Category.
    """

    class Meta:
        verbose_name = "SubCategory"
        verbose_name_plural = "SubCategories"

    title = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to=upload_image_subcategory_path, null=True, blank=True
    )

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="subcategories"
    )

    def __str__(self):
        return self.title
