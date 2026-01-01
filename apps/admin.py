from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin

from apps.models import User, Category, Product, Order


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('id', 'is_staff', 'is_active')


@admin.register(Category)
class CategoryModelAdmin(ModelAdmin):
    model = Category
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


@admin.register(Product)
class ProductModelAdmin(ModelAdmin):
    model = Product
    list_display = ('id', 'name', "quantity", "arrival_price", "sales_price", "kaspi_price", "category",)
    list_display_links = ('id', 'name')


@admin.register(Order)
class OrderModelAdmin(ModelAdmin):
    model = Order
    list_display = ('id', 'product', 'quantity', 'deadline', 'price_type', 'price')
    list_display_links = ('id', 'product')
    readonly_fields = ('price',)

    def save_model(self, request, obj, form, change):
        if obj.price_type == 'sales':
            obj.price = obj.product.sales_price
        else:
            obj.price = obj.product.kaspi_price

        if obj.quantity > obj.product.quantity:
            messages.warning(request,
                             f"Количество товара недостаточно! В настоящее время доступно {obj.product.quantity}. Количество не уменьшилось."
                             )
            self._order_not_created = True
            return

        obj.product.quantity -= obj.quantity
        obj.product.save()
        super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        if getattr(self, '_order_not_created', False):
            return self.response_post_save_add(request, None)

        return super().response_add(request, obj, post_url_continue)
