from decimal import Decimal

from django.contrib import admin
from django.db.models import DecimalField
from django.db.models import F
from django.db.models import Sum

from rudik.admin import rudik_site

from .models import Order
from .models import ProductVariantOrder
from .models import Recipient


class ProductTabularInline(admin.TabularInline):
    model = ProductVariantOrder
    extra = 0


@admin.register(Order, site=rudik_site)
class OrderModelAdmin(admin.ModelAdmin):
    inlines = [ProductTabularInline]
    list_display = ["__str__", "recipient", "status", "amount", "created"]
    list_editable = ["status"]
    list_filter = ["status"]

    def amount(self, order):
        data = order.productvariantorder_set.aggregate(
            amount=Sum(F("qty") * F("product_variant__price"), output_field=DecimalField())
        )
        return Decimal(data["amount"]).quantize(Decimal(".01"))

    def get_queryset(self, request):
        queryset = super(OrderModelAdmin, self).get_queryset(request)
        return queryset.order_by("-id")


@admin.register(Recipient, site=rudik_site)
class RecipientModelAdmin(admin.ModelAdmin):
    pass
