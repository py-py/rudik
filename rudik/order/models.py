from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import DecimalField
from django.db.models import F
from django.db.models import Sum
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from .constants import DELIVERY_COMPANIES
from .constants import DELIVERY_COMPANY_UKRPOSHTA
from .constants import DELIVERY_TYPES
from .constants import NOTIFICATION_TYPE_EMAIL
from .constants import NOTIFICATION_TYPE_SMS
from .constants import NOTIFICATION_TYPES
from .constants import PAYMENT_TYPES
from .constants import STATUS_NEW
from .constants import STATUS_WAIT_FOR_PAYMENT
from .constants import STATUSES
from .integrations import EPochtaClient


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
    ttn = models.CharField(max_length=64, null=True, blank=True)

    region = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    branch = models.CharField(max_length=256)

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

    @cached_property
    def amount(self):
        data = self.items.aggregate(
            amount=Sum(F("qty") * F("product_variant__price"), output_field=DecimalField())
        )
        return Decimal(data["amount"]).quantize(Decimal(".01"))

    @property
    def main_recipient(self):
        if self.second_recipient:
            return self.second_recipient
        return self.recipient

    def notify(self):
        notification = self.notifications.create(notification_type=NOTIFICATION_TYPE_SMS)
        notification.do_emit()


class Notification(TimeStampedModel, models.Model):
    order = models.ForeignKey(
        "order.Order", on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.PositiveSmallIntegerField(
        choices=NOTIFICATION_TYPES, default=NOTIFICATION_TYPE_SMS
    )
    text = models.TextField()
    campaign_id = models.CharField(max_length=65, null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        contact = self.get_recipient_contact()
        return f"{self.get_notification_type_display()} to {contact}"

    def clean(self):
        if self.notification_type == NOTIFICATION_TYPE_EMAIL:
            if not self.order.main_recipient.email:
                raise ValidationError({"order": _("Recipient in order has not inputted email.")})

    @property
    def client(self):
        return EPochtaClient()

    def get_recipient_contact(self):
        if self.notification_type == NOTIFICATION_TYPE_SMS:
            return self.order.main_recipient.phone
        elif self.notification_type == NOTIFICATION_TYPE_EMAIL:
            return self.order.main_recipient.email
        else:
            raise ValueError("Not found notification type.")

    def do_emit(self):
        if self.notification_type == NOTIFICATION_TYPE_SMS and self.can_be_emitted():
            phone = self.order.main_recipient.phone
            template = self.get_sms_template()
            text = render_to_string(template, context=self.get_context()).replace("\n", " ")
            data = self.client.send_sms(phone, text)
            self.campaign_id = data["id"]
            self.save(update_fields=["campaign_id"])

    def get_context(self):
        return {
            "order_id": self.order.id,
            "summa": self.order,
            "ttn": self.order.ttn,
            "card_bank": "PrivatBank",
            "card_number": "5000400030002000",
            "card_owner": "Ivanov I.I.",
            "site_url": "rudik.com.ua",
        }

    def can_be_emitted(self):
        return self.order.status in [STATUS_NEW, STATUS_WAIT_FOR_PAYMENT]

    def get_sms_template(self):
        if self.order.status == STATUS_NEW:
            template = "order/sms/new_order_ttn"
        elif self.order.status == STATUS_WAIT_FOR_PAYMENT:
            template = "order/sms/new_order_card"
        else:
            raise NotImplementedError
        return template
