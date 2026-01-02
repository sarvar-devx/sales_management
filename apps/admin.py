from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.db.models.functions import TruncDate
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


@admin.register(Order)
class OrderModelAdmin(ModelAdmin):
    model = Order
    list_display = ('id', 'product', 'quantity', 'deadline', 'price_type', 'price', 'status')
    list_display_links = ('id', 'product')
    readonly_fields = ('price', 'status',)
    list_filter = ('product', 'price_type', 'status')
    ordering = ('deadline',)
    actions = ['mark_as_finished']

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
