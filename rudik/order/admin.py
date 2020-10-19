from decimal import Decimal

from django.contrib import admin
from django.db.models import DecimalField
from django.db.models import F
from django.db.models import Sum
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from core.admin import PreviewSingleObjectMixin
from rudik.admin import rudik_site

from .models import Order
from .models import OrderItem
from .models import Recipient


class OrderItemTabularInline(PreviewSingleObjectMixin, admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["price_per_item"]

    def price_per_item(self, item):
        return item.product_variant.price

    price_per_item.short_description = _("Price Per Item")

    def get_image_url(self, order_item):
        return order_item.product_variant.default_image.url


@admin.register(Order, site=rudik_site)
class OrderModelAdmin(admin.ModelAdmin):
    inlines = [OrderItemTabularInline]
    list_display = ["__str__", "recipient", "status", "amount", "previews", "created"]
    list_editable = ["status"]
    list_filter = ["status", "delivery_company"]
    readonly_fields = ["amount", "dont_call", "previews"]
    search_fields = [
        "id",
        "recipient__first_name",
        "recipient__second_name",
        "recipient__phone",
        "recipient__email",
    ]

    fieldsets = [
        [_("Main"), {"fields": ["amount", "status", "dont_call"], "classes": ["required"]}],
        [_("Recipient"), {"fields": ["recipient", "second_recipient"]}],
        [
            _("Delivery"),
            {
                "fields": [
                    "delivery_company",
                    "delivery_type",
                    "payment_type",
                    "branch",
                    "region",
                    "city",
                ]
            },
        ],
        [_("Comment"), {"fields": ["comment"]}],
    ]

    def get_queryset(self, request):
        queryset = super(OrderModelAdmin, self).get_queryset(request)
        return queryset.order_by("-id")

    @staticmethod
    def amount(order):
        data = order.items.aggregate(
            amount=Sum(F("qty") * F("product_variant__price"), output_field=DecimalField())
        )
        return Decimal(data["amount"]).quantize(Decimal(".01"))

    @staticmethod
    def previews(order):
        context = {"items": order.items.all(), "height": 100}
        return render_to_string("order/admin/previews.html", context=context)


@admin.register(Recipient, site=rudik_site)
class RecipientModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "first_name", "second_name", "orders"]

    @staticmethod
    def orders(recipient):
        return recipient.orders.count()

    orders.short_description = _("Orders")
