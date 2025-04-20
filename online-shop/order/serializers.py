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


class OrderUpdateSerializer(serializers.Serializer):
    deliveryType = serializers.ChoiceField(choices=["express", "standard"])
    city = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=255)
    paymentType = serializers.CharField(max_length=50)
    products = ProductSerializer(many=True)