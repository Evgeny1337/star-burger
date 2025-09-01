from rest_framework import serializers
from .models import Order,OrderProduct
from django.db import transaction

class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product','quantity']


    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Количество должно быть положительным числом')
        return value


class OrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    products = OrderProductSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['id','firstname', 'lastname', 'phonenumber', 'address', 'products']

    def create(self, validated_data):
        with transaction.atomic():
            order = Order.objects.create(
                firstname=validated_data['firstname'],
                lastname=validated_data['lastname'],
                phonenumber=validated_data['phonenumber'],
                address=validated_data['address'],
            )
            order_products = []
            for product in validated_data['products']:
                order_product = OrderProduct(
                    order=order,
                    product=product['product'],
                    quantity=product['quantity'],
                    fixed_price=product['product'].price,
                )
                order_products.append(order_product)
            OrderProduct.objects.bulk_create(order_products)
            return order

    def validate_firstname(self, value):
        if not value.strip():
            raise serializers.ValidationError('Имя не может быть пустым')
        return value

    def validate_address(self, value):
        print(value)
        if not value.strip():
            raise serializers.ValidationError('Адрес не может быть пустым')
        return value

