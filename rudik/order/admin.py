from decimal import Decimal

from django.contrib import admin
from django.db.models import DecimalField
from django.db.models import F
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from core.admin import PreviewMixin
from rudik.admin import rudik_site

from .models import Order
from .models import OrderItem
from .models import Recipient


class OrderItemTabularInline(PreviewMixin, admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["price_per_item"]

    def price_per_item(self, item):
        return item.product_variant.price

    price_per_item.short_description = _("Price Per Item")

    def get_image_url(self, order_item):
        return order_item.product_variant.images.get(is_default=True).image.url


@admin.register(Order, site=rudik_site)
class OrderModelAdmin(admin.ModelAdmin):
    inlines = [OrderItemTabularInline]
    list_display = ["__str__", "recipient", "status", "amount", "created"]
    list_editable = ["status"]
    list_filter = ["status"]

    def amount(self, order):
        data = order.items.aggregate(
            amount=Sum(F("qty") * F("product_variant__price"), output_field=DecimalField())
        )
        return Decimal(data["amount"]).quantize(Decimal(".01"))

    def get_queryset(self, request):
        queryset = super(OrderModelAdmin, self).get_queryset(request)
        return queryset.order_by("-id")


@admin.register(Recipient, site=rudik_site)
class RecipientModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "first_name", "second_name", "orders"]

    @staticmethod
    def orders(recipient):
        return recipient.orders.count()

    orders.short_description = _("Orders")
