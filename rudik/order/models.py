from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from .constants import DELIVERY_COMPANIES
from .constants import DELIVERY_COMPANY_UKRPOSHTA
from .constants import DELIVERY_TYPES
from .constants import PAYMENT_TYPES


class Recipient(TimeStampedModel, models.Model):
    first_name = models.CharField(max_length=256)
    second_name = models.CharField(max_length=256)
    phone = models.CharField(max_length=256)
    email = models.EmailField(null=True, blank=True)


class Order(TimeStampedModel, models.Model):
    recipient = models.ForeignKey("order.Recipient", on_delete=models.PROTECT)
    second_recipient = models.ForeignKey(
        "order.Recipient", on_delete=models.PROTECT, null=True, blank=True
    )
    payment_type = models.PositiveSmallIntegerField(choices=PAYMENT_TYPES)
    delivery_company = models.PositiveSmallIntegerField(choices=DELIVERY_COMPANIES)
    delivery_type = models.PositiveSmallIntegerField(choices=DELIVERY_TYPES)

    region = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    branch = models.CharField(max_length=256)

    comment = models.TextField()
    dont_call = models.BooleanField(default=False)

    def clean(self):
        if self.delivery_company == DELIVERY_COMPANY_UKRPOSHTA:
            if not self.region:
                raise ValidationError({"region": _("This field is required.")})
