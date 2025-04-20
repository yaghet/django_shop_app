from typing import Optional

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from catalog.models import Category, SubCategory


class SubCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = ["id", "title", "image"]

    @extend_schema_field(serializers.DictField(child=serializers.CharField(), allow_null=True))
    def get_image(self, obj) -> Optional[dict[str, str]]:
        if obj.image:
            return {
                "src": obj.image.url,
                "alt": obj.image.name,
            }
        else:
            return None


class CategorySerializer(serializers.ModelSerializer):

    subcategories = SubCategorySerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "title", "subcategories", "image"]

    @extend_schema_field(serializers.DictField(child=serializers.CharField(), allow_null=True))
    def get_image(self, obj) -> Optional[dict[str, str]]:
        if obj.image:
            return {
                "src": obj.image.url,
                "alt": obj.image.name,
            }
        else:
            return None
