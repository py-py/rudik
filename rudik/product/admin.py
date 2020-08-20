from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from rudik.admin import rudik_site

from .models import Category
from .models import CategoryImage
from .models import Color
from .models import Product
from .models import ProductImage


@admin.register(Color, site=rudik_site)
class ColorAdmin(admin.ModelAdmin):
    list_display = ["__str__", "color"]


class CategoryImageTabularInline(admin.TabularInline):
    model = CategoryImage
    extra = 1


@admin.register(Category, site=rudik_site)
class CategoryAdmin(MPTTModelAdmin):
    inlines = [CategoryImageTabularInline]


class ProductImageTabularInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product, site=rudik_site)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageTabularInline]
