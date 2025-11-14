from django.contrib import admin
from django.http.response import HttpResponseRedirect
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.exceptions import ObjectDoesNotExist
from .models import Product, OrderProduct
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from .models import Order


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0





@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


class OrderProductInline(admin.TabularInline):  # или admin.StackedInline
    model = OrderProduct
    extra = 1
    min_num = 1
    fields = ('product', 'quantity', 'product_price_display')
    readonly_fields = ('product_price_display',)

    def product_price_display(self, obj):
        if obj.product:
            return f"{obj.fixed_price} ₽"
        return "-"

    product_price_display.short_description = 'Цена товара'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    pass




@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # TODO Доабвить total price
    list_display = ('id','firstname','lastname','phonenumber','address', 'status', 'comment', 'registered_at', 'called_at', 'delivered_at', 'cooking_restaurant')
    list_filter = ('status',)
    list_editable = ('status',)
    inlines = (OrderProductInline,)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "cooking_restaurant":
            object_id = request.resolver_match.kwargs.get('object_id')
            if object_id:
                try:
                    order = Order.objects.get(id=object_id)
                    available_restaurants = self.get_available_restaurants(order)
                    kwargs["queryset"] = available_restaurants
                except ObjectDoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_available_restaurants(self, order):
        menu_items = RestaurantMenuItem.objects.filter(
            availability=True
        )
        product_restaurants = {}
        for item in menu_items:
            if item.product_id not in product_restaurants:
                product_restaurants[item.product_id] = []
            product_restaurants[item.product_id].append(item.restaurant_id)

        available_restaurant_ids = None
        for order_product in order.order_products.all():
            product_id = order_product.product_id
            if product_id in product_restaurants:
                restaurant_ids = set(product_restaurants[product_id])
                if available_restaurant_ids is None:
                    available_restaurant_ids = restaurant_ids
                else:
                    available_restaurant_ids = available_restaurant_ids.intersection(restaurant_ids)
            else:
                return Restaurant.objects.none()
            if not available_restaurant_ids:
                return Restaurant.objects.none()
        return Restaurant.objects.filter(id__in=available_restaurant_ids)


    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, OrderProduct) and not instance.pk:
                instance.fixed_price = instance.product.price
        super().save_formset(request, form, formset, change)

    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        if '_continue' not in request.POST and '_addanother' not in request.POST and isinstance(response, HttpResponseRedirect):
            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
                return HttpResponseRedirect(next_url)

        return response


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'quantity', 'order', 'product')

