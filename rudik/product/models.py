import os

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


def upload_to(instance, filename):
    return os.path.join(instance.upload_folder, filename)


class AbstractImage(TimeStampedModel, models.Model):
    upload_folder = None
    fk_field = None

    image = models.ImageField(upload_to=upload_to)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        queryset = getattr(self, self.fk_field).images.all()
        if self.is_default:
            queryset.update(is_default=False)
        else:
            if not queryset.filter(is_default=True).exists():
                self.is_default = True
        super(AbstractImage, self).save(*args, **kwargs)


class CategoryImage(AbstractImage):
    upload_folder = "category"
    fk_field = "category"

    category = models.ForeignKey(
        "product.Category", on_delete=models.CASCADE, related_name="images"
    )


class ProductImage(AbstractImage):
    upload_folder = "product"
    fk_field = "product"

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
    category = models.ForeignKey(
        "product.Category", on_delete=models.PROTECT, related_name="products"
    )

    def __str__(self):
        return self.name


class ConfigurationType(TimeStampedModel, models.Model):
    name = models.CharField(max_length=256)
    is_color = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Configuration(TimeStampedModel, models.Model):
    type = models.ForeignKey("product.ConfigurationType", on_delete=models.CASCADE)
    name = models.CharField(max_length=256, null=True, blank=True)
    value = models.CharField(max_length=256)

    def __str__(self):
        return "{} ({})".format(self.type.name, self.name or self.value)

    def clean(self):
        if self.type.is_color and not self.name:
            raise ValidationError({"name": _("This field is required.")})


class ProductVariant(TimeStampedModel, models.Model):
    product = models.ForeignKey(
        "product.Product", on_delete=models.CASCADE, related_name="variants"
    )
    configurations = models.ManyToManyField("product.Configuration")
    qty = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_price = models.DecimalField(max_digits=8, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.product.name

    @property
    def cost(self):
        return self.purchase_price + self.delivery_price

    @property
    def margin(self):
        return self.price - self.cost
