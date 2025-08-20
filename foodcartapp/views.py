import phonenumbers
from django.http import JsonResponse
from django.db import transaction
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Order, OrderProduct
from .serializers import OrderSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })

@api_view(['GET','POST'])
def register_order(request):
    if request.method == 'GET':
        orders = Order.objects.prefetch_related('order_products')
        orders_response = []
        for order in orders:
            products = []
            for order_product in order.order_products.all():
                products.append({
                'id': order_product.id,
                'name': order_product.product.name,
                'price': order_product.product.price,
                'quantity': order_product.quantity,
                })
            orders_response.append({
            'id': order.id,
            'first_name': order.firstname,
            'last_name': order.lastname,
            'phonenumber': str(order.phonenumber),
            'address': order.address,
            'products': products
            })
        return Response(orders_response)
    if request.method  == 'POST':
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            order = Order.objects.create(
                firstname=serializer.validated_data['firstname'],
                lastname=serializer.validated_data['lastname'],
                phonenumber=serializer.validated_data['phonenumber'],
                address=serializer.validated_data['address']
            )
            OrderProduct.objects.bulk_create([
                OrderProduct(
                    order=order,
                    product=product_data['product'],
                    quantity=product_data['quantity']
                ) for product_data in serializer.validated_data['products']
            ])

        return Response({'id': order.id, **serializer.data}, status=status.HTTP_201_CREATED)





