from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.aggregates import Sum
from django.db.models.expressions import F
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone

class OrderQuerySet(models.QuerySet):
    def with_total_price(self):
        return self.annotate(
            total_price=Sum(F('order_products__quantity') * F('order_products__product__price'))
        )

class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    class Status(models.TextChoices):
        UNPROCESSED = 'unprocessed', 'Необработанный'
        PROCESSING = 'processing', 'В обработке'
        IN_DELIVERY = 'in_delivery', 'В доставке'
        COMPLETED = 'completed', 'Выполнен'
        CANCELLED = 'cancelled', 'Отменен'

    firstname = models.CharField(
        'Имя',
        max_length=100
    )
    lastname = models.CharField(
        'Фамилия',
        max_length=100,
        blank=True,
        default='-'
    )
    phonenumber = PhoneNumberField(
        'Телефон',
        region='RU'
    )
    address = models.CharField(
        'Адрес доставки',
        max_length=250,
        default='-'
    )

    status = models.CharField(
        'Статус заказа',
        max_length=20,
        choices=Status.choices,
        default=Status.UNPROCESSED,
        db_index=True
    )

    comment = models.TextField(
        'Комментарий',
        blank=True,
        null=True,
        default='-',
    )

    registrated_at = models.DateTimeField(
        'Дата и время создания заказа',
        default=timezone.now,
        db_index=True
    )

    called_at = models.DateTimeField(
        'Дата и время звонка',
        null=True,
        blank=True,
        db_index=True
    )


    delivered_at = models.DateTimeField(
        'Дата и время доставки',
        null=True,
        blank=True,
        db_index=True
    )

    @property
    def status_label(self):
        return self.get_status_display()

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

        indexes = [
            models.Index(fields=['status'])
        ]

    def __str__(self):
        return f"{self.firstname} {self.lastname} - {self.status}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='order_items')
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
    )
    fixed_price = models.DecimalField(
        'Фиксированная цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        default=0.00
    )

    class Meta:
        verbose_name = 'Продукт в заказе'
        verbose_name_plural = 'Продукты в заказе'

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
