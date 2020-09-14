from django.contrib import admin

from rudik.admin import rudik_site

from .models import Order
from .models import ProductOrder
from .models import Recipient


class ProductTabularInline(admin.TabularInline):
    model = ProductOrder
    extra = 0


@admin.register(Order, site=rudik_site)
class OrderModelAdmin(admin.ModelAdmin):
    inlines = [ProductTabularInline]


@admin.register(Recipient, site=rudik_site)
class RecipientModelAdmin(admin.ModelAdmin):
    pass
