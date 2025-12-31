from django.contrib import admin
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
    list_display = ('id', 'product', 'quantity', 'deadline', 'price')
    list_display_links = ('id', 'product')
