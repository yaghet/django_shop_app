from rest_framework import serializers

from order.models import Order
from product.serializers import ProductSerializer


class OrderSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, required=True)
    fullName = serializers.StringRelatedField()
    email = serializers.StringRelatedField()
    phone = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = "__all__"
