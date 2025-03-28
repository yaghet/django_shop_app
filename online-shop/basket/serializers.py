from rest_framework import serializers

from basket.models import BasketItem
from product.serializers import ProductSerializer


class BasketItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItem
        fields = ['id', 'product', 'amount']

    def to_representation(self, instance):
        data = ProductSerializer(instance.product).data
        data['count'] = instance.amount
        return data
