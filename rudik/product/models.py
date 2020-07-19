from django.db import models
from model_utils.models import TimeStampedModel


class Category(TimeStampedModel, models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Product(TimeStampedModel, models.Model):
    name = models.CharField(max_length=256)
    category = models.ForeignKey(
        "product.Category", on_delete=models.PROTECT, related_name="products"
    )

    def __str__(self):
        return self.name
