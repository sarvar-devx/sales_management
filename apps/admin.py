from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.db.models.functions import TruncDate
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.html import format_html

from apps.models import User, Category, Product, Order, Expense


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
    list_display = ('id', 'name', "quantity", "category", "arrival_price", "sales_price", "kaspi_price")
    list_display_links = ('id', 'name')

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)

        if is_new:
            Expense.objects.create(
                product=obj,
                quantity=obj.quantity,
                amount=obj.arrival_price * obj.quantity,
                date=obj.created_at
            )


# @admin.register(Order)
# class OrderModelAdmin(ModelAdmin):
#     model = Order
#     list_display = ('id', 'product', 'quantity', 'deadline', 'price_type', 'price', 'status')
#     list_display_links = ('id', 'product')
#     readonly_fields = ('price', 'status',)
#     list_filter = ('product', 'price_type', 'status')
#     ordering = ('deadline',)
#     actions = ['mark_as_finished']
#
#     def save_model(self, request, obj, form, change):
#         if obj.price_type == 'sales':
#             obj.price = obj.product.sales_price
#         else:
#             obj.price = obj.product.kaspi_price
#
#         if obj.quantity > obj.product.quantity:
#             messages.warning(request,
#                              f"Количество товара недостаточно! В настоящее время доступно {obj.product.quantity}. Количество не уменьшилось."
#                              )
#             self._order_not_created = True
#             return
#
#         obj.product.quantity -= obj.quantity
#         obj.product.save()
#         super().save_model(request, obj, form, change)
#
#     def response_add(self, request, obj, post_url_continue=None):
#         if getattr(self, '_order_not_created', False):
#             return self.response_post_save_add(request, None)
#
#         return super().response_add(request, obj, post_url_continue)
#
#     def mark_as_finished(self, request, queryset):
#         updated = queryset.update(status='finished')
#         self.message_user(request, f"{updated} заказ(ов) помечено как завершённые.")
#
#     mark_as_finished.short_description = "Пометить выбранные заказы как завершённые"


@admin.register(Order)
class OrderModelAdmin(ModelAdmin):
    model = Order
    list_display = ('id', 'product', 'quantity', 'deadline', 'price_type', 'price', 'status', 'mark_finished_button')
    list_display_links = ('id', 'product')
    readonly_fields = ('price', 'status',)
    list_filter = ('product', 'price_type', 'status')
    ordering = ('deadline',)
    actions = ['mark_as_finished']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if 'status__exact' not in request.GET:
            return qs.filter(status='new')
        return qs

    def mark_finished_button(self, obj):
        if obj.status != 'finished':
            return format_html(
                '<a href="{}" style="color: green; font-size: 18px;">✅</a>',
                f'mark_finished/{obj.id}/'
            )
        return "❌"

    mark_finished_button.short_description = ''
    mark_finished_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('mark_finished/<int:order_id>/', self.admin_site.admin_view(self.process_mark_finished),
                 name='mark_finished'),
        ]
        return custom_urls + urls

    def process_mark_finished(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'finished'
            order.save()
            messages.success(request, f'Заказ #{order.id} завершён.')
        except Order.DoesNotExist:
            messages.error(request, 'Заказ не найден.')

        return HttpResponseRedirect('../../')

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

    def mark_as_finished(self, request, queryset):
        updated = queryset.update(status='finished')
        self.message_user(request, f"{updated} заказ(ов) помечено как завершённые.")

    mark_as_finished.short_description = "Пометить выбранные заказы как завершённые"


class ExactDateFilter(SimpleListFilter):
    title = 'Дата'
    parameter_name = 'date'

    def lookups(self, request, model_admin):
        dates = (
            Expense.objects
            .annotate(day=TruncDate('date'))
            .values_list('day', flat=True)
            .distinct()
            .order_by('day')
        )
        return [(d, d.strftime('%d.%m.%Y')) for d in dates]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__date=self.value())
        return queryset


@admin.register(Expense)
class ExpenseModelAdmin(ModelAdmin):
    model = Expense
    list_display = ('id', 'product', 'quantity', 'amount', 'date')
    list_filter = (ExactDateFilter,)
    ordering = ('-date',)
