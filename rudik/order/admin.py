from decimal import Decimal

from django.contrib import admin
from django.db.models import DecimalField
from django.db.models import F
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import path
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from core.admin import PreviewSingleObjectMixin
from rudik.admin import rudik_site

from .models import Notification
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
    change_form_template = "order/admin/change_form.html"
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

    def get_urls(self):
        urls = super(OrderModelAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        return [
            path(
                "<path:object_id>/notifications/",
                self.admin_site.admin_view(self.notification_view),
                name="%s_%s_notifications" % info,
            ),
        ] + urls

    def notification_view(self, request, *args, **kwargs):
        url = reverse("admin:order_notification_changelist")
        url += "?order_id={}".format(kwargs["object_id"])
        return HttpResponseRedirect(url)


@admin.register(Recipient, site=rudik_site)
class RecipientModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "first_name", "second_name", "orders"]

    @staticmethod
    def orders(recipient):
        return recipient.orders.count()

    orders.short_description = _("Orders")


@admin.register(Notification, site=rudik_site)
class NotificationModelAdmin(admin.ModelAdmin):
    list_display = ["recipient", "notification_type", "order", "is_sent", "timestamp"]
    readonly_fields = ["is_sent"]

    @staticmethod
    def recipient(notification):
        return notification.order.get_recipient_phone()

    @staticmethod
    def timestamp(notification):
        return notification.created

    timestamp.short_description = _("Timestamp")

    def get_queryset(self, request):
        queryset = super(NotificationModelAdmin, self).get_queryset(request)
        order_id = request.GET.get("order_id")
        if order_id and order_id.isdigit():
            queryset = queryset.filter(order_id=order_id)
        return queryset
