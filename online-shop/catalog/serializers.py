from rest_framework import serializers

from catalog.models import Category, SubCategory


class SubCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = ["id", "title", "image"]

    def get_image(self, obj):
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

    def get_image(self, obj):
        if obj.image:
            return {
                "src": obj.image.url,
                "alt": obj.image.name,
            }
        else:
            return None
