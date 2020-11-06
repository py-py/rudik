from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from .clients import SendPulseClient
from .constants import DELIVERY_COMPANIES
from .constants import DELIVERY_COMPANY_UKRPOSHTA
from .constants import DELIVERY_TYPES
from .constants import NOTIFICATION_TYPE_SMS
from .constants import NOTIFICATION_TYPES
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

    def get_name(self):
        return "{} {}".format(self.first_name, self.second_name)

    @classmethod
    def create_recipient(cls, phone, kwargs):
        recipient, _ = cls.objects.update_or_create(phone=phone, defaults=kwargs)
        return recipient

    def count_orders(self):
        return self.orders.count()


class OrderItem(TimeStampedModel, models.Model):
    product_variant = models.ForeignKey("product.ProductVariant", on_delete=models.CASCADE)
    order = models.ForeignKey("order.Order", on_delete=models.CASCADE, related_name="items")
    qty = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ("product_variant", "order")

    def clean(self):
        if self.product_variant.count_rest() < self.qty:
            raise ValidationError({"qty": _("Not enough in warehouse.")})


class Order(TimeStampedModel, models.Model):
    recipient = models.ForeignKey(
        "order.Recipient", on_delete=models.PROTECT, related_name="orders"
    )
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
        "product.ProductVariant", through="order.OrderItem", related_name="orders"
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

    def get_recipient_phone(self):
        if self.second_recipient:
            return self.second_recipient.phone
        return self.recipient.phone


class Notification(TimeStampedModel, models.Model):
    order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.PositiveSmallIntegerField(
        choices=NOTIFICATION_TYPES, default=NOTIFICATION_TYPE_SMS
    )
    text = models.TextField()
    is_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    @property
    def client(self):
        return SendPulseClient()

    def emit(self):
        self.client.send_sms()
        self.is_sent = True
        self.save(update_fields=["is_sent"])
