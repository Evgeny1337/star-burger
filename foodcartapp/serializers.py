from rest_framework import serializers
from .models import Order,OrderProduct

class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product','quantity']


    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Количество должно быть положительным числом')
        return value


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']

    def validate_firstname(self, value):
        if not value.strip():
            raise serializers.ValidationError('Имя не может быть пустым')
        return value

    def validate_address(self, value):
        print(value)
        if not value.strip():
            raise serializers.ValidationError('Адрес не может быть пустым')
        return value
