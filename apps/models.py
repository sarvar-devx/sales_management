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
        verbose_name="Login",
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
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(TimeBaseModel):
    name = CharField(max_length=255)
    arrival_price = PositiveIntegerField()
    sales_price = PositiveIntegerField()
    kaspi_price = PositiveIntegerField()
    category = ForeignKey("apps.Category", CASCADE)
    quantity = PositiveIntegerField()

    def __str__(self):
        return self.name


class Order(TimeBaseModel):
    product = ForeignKey("apps.Product", CASCADE)
    quantity = PositiveIntegerField()
    deadline = DateTimeField()
    price = PositiveIntegerField()

    def __str__(self):
        return self.product.name
