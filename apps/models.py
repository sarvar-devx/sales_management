from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator as username_validator
from django.db.models import Model, ForeignKey, CASCADE
from django.db.models.fields import CharField, DateTimeField, PositiveIntegerField, EmailField


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

    def __str__(self):
        return self.name


class Product(TimeBaseModel):
    name = CharField(max_length=255, verbose_name="Название")
    arrival_price = PositiveIntegerField(verbose_name="Цена прибытия")
    sales_price = PositiveIntegerField(verbose_name="Цена продажи")
    kaspi_price = PositiveIntegerField(verbose_name="Каспи цена")
    category = ForeignKey("apps.Category", CASCADE, verbose_name="Категория")
    quantity = PositiveIntegerField(verbose_name="Количество")

    def __str__(self):
        return self.name


class Order(TimeBaseModel):
    PRICE_TYPE_CHOICES = (
        ('sales', 'Цена продажи'),
        ('kaspi', 'Каспи цена'),
    )
    product = ForeignKey("apps.Product", CASCADE, verbose_name="Продукт")
    quantity = PositiveIntegerField(verbose_name="Количество")
    deadline = DateTimeField(verbose_name="Срок")
    price_type = CharField(
        max_length=10,
        choices=PRICE_TYPE_CHOICES,
        verbose_name="Тип цены"
    )
    price = PositiveIntegerField(editable=False, verbose_name="Цена")

    def __str__(self):
        return self.product.name
