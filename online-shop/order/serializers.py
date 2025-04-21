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

    createdAt = serializers.DateTimeField()
    fullName = serializers.CharField(min_length=2, max_length=20)
    email = serializers.EmailField()
    phone = serializers.RegexField(
        regex=r'^\+?\d{10,12}$',
        error_messages={'invalid': 'Invalid phone number.'}
    )
    deliveryType = serializers.ChoiceField(choices=["free", "express", 'ordinary'])
    paymentType = serializers.ChoiceField(choices=["online", "cash", "card"])
    city = serializers.CharField(min_length=2, max_length=40)
    address = serializers.CharField(min_length=10, max_length=200)
