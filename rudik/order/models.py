from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from .constants import DELIVERY_COMPANIES
from .constants import DELIVERY_COMPANY_UKRPOSHTA
from .constants import DELIVERY_TYPES
from .constants import PAYMENT_TYPES
from .constants import STATUS_NEW
from .constants import STATUSES


class Recipient(TimeStampedModel, models.Model):
    first_name = models.CharField(max_length=256)
    second_name = models.CharField(max_length=256)
    phone = PhoneNumberField(unique=True)
    email = models.EmailField(null=True, blank=True)

    class Meta:
        verbose_name = _("Recipient")
        verbose_name_plural = _("Recipients")

    def __str__(self):
        return self.phone.as_international

    @classmethod
    def create_recipient(cls, phone, kwargs):
        recipient, _ = cls.objects.update_or_create(phone=phone, defaults=kwargs)
        return recipient


class ProductVariantOrder(TimeStampedModel, models.Model):
    product_variant = models.ForeignKey("product.ProductVariant", on_delete=models.CASCADE)
    order = models.ForeignKey("order.Order", on_delete=models.CASCADE)
    qty = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ("product_variant", "order")


class Order(TimeStampedModel, models.Model):
    recipient = models.ForeignKey("order.Recipient", on_delete=models.PROTECT)
    second_recipient = models.ForeignKey(
        "order.Recipient",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="secondary_orders",
    )
    delivery_company = models.PositiveSmallIntegerField(choices=DELIVERY_COMPANIES)
    delivery_type = models.PositiveSmallIntegerField(choices=DELIVERY_TYPES)
    payment_type = models.PositiveSmallIntegerField(choices=PAYMENT_TYPES)
    branch = models.CharField(max_length=256)

    region = models.CharField(max_length=256)
    city = models.CharField(max_length=256)

    comment = models.TextField(null=True, blank=True)
    dont_call = models.BooleanField(default=False)
    status = models.PositiveSmallIntegerField(choices=STATUSES, default=STATUS_NEW)
    products = models.ManyToManyField(
        "product.ProductVariant", through="order.ProductVariantOrder", related_name="orders"
    )

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return str(self.id)

    def clean(self):
        if self.delivery_company == DELIVERY_COMPANY_UKRPOSHTA:
            if not self.region:
                raise ValidationError({"region": _("This field is required.")})
