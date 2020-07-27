from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class CategoryImage(TimeStampedModel, models.Model):
    image = models.ImageField()
    category = models.ForeignKey(
        "product.Category", on_delete=models.CASCADE, related_name="images"
    )


class ProductImage(TimeStampedModel, models.Model):
    image = models.ImageField()
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE, related_name="images")


class Category(TimeStampedModel, MPTTModel):
    name = models.CharField(max_length=256, unique=True)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name


class Product(TimeStampedModel, models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField()
    category = models.ForeignKey(
        "product.Category", on_delete=models.PROTECT, related_name="products"
    )

    def __str__(self):
        return self.name
