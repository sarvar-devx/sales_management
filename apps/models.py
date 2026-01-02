from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator as username_validator
from django.db.models import Model, ForeignKey, CASCADE
from django.db.models.fields import CharField, DateTimeField, PositiveIntegerField, EmailField, DateField


class TimeBaseModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    username = CharField(
        verbose_name="Логин",
        max_length=150,
        unique=True,
        help_text="Обязательно. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.",
        validators=[username_validator()],
        error_messages={
            "unique": "Пользователь с таким именем пользователя уже существует.",
        },
    )
    email = EmailField(
        blank=True,
        null=True,
    )


class Category(Model):
    name = CharField(max_length=255, verbose_name="Название")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(TimeBaseModel):
    name = CharField(max_length=255, verbose_name="Название")
    arrival_price = PositiveIntegerField(verbose_name="Цена прибытия")
    sales_price = PositiveIntegerField(verbose_name="Цена продажи")
    kaspi_price = PositiveIntegerField(verbose_name="Каспи цена")
    category = ForeignKey("apps.Category", CASCADE, verbose_name="Категория")
    quantity = PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.name


class Order(TimeBaseModel):
    PRICE_TYPE_CHOICES = (
        ('sales', 'Цена продажи'),
        ('kaspi', 'Каспи цена'),
    )
    STATUS_CHOICES = (
        ('new', 'Новый ✅'),
        ('finished', 'Завершён ❌'),
    )
    product = ForeignKey("apps.Product", CASCADE, verbose_name="Продукт")
    quantity = PositiveIntegerField(verbose_name="Количество")
    deadline = DateField(verbose_name="Срок")
    price_type = CharField(
        max_length=10,
        choices=PRICE_TYPE_CHOICES,
        verbose_name="Тип цены"
    )
    price = PositiveIntegerField(editable=False, verbose_name="Цена")
    status = CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return self.product.name


class Expense(Model):
    product = ForeignKey(Product, CASCADE, verbose_name="Продукт")
    quantity = PositiveIntegerField(verbose_name="Количество")
    amount = PositiveIntegerField(verbose_name="Сумма")
    date = DateTimeField(verbose_name="Дата")

    class Meta:
        verbose_name = "Расход"
        verbose_name_plural = "Расходы"

    def __str__(self):
        return f"{self.product.name} — {self.amount}"
