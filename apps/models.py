from django.db.models import Model, ForeignKey, CASCADE
from django.db.models.fields import CharField, DateTimeField, DecimalField, PositiveIntegerField


class TimeBaseModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(Model):
    name = CharField(max_length=255)


class Product(TimeBaseModel):
    name = CharField(max_length=255)
    arrival_price = DecimalField()
    sales_price = DecimalField()
    kaspi_price = DecimalField()
    category = ForeignKey("apps.Category", CASCADE)


class Order(TimeBaseModel):
    product = ForeignKey("apps.Product", CASCADE)
    quantity = PositiveIntegerField()
    deadline = DateTimeField()
