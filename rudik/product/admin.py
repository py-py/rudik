from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from rudik.admin import rudik_site

from .models import Category
from .models import CategoryImage
from .models import Product
from .models import ProductImage


class ProductImageAdmin(admin.TabularInline):
    model = ProductImage
    extra = 1


class CategoryImageAdmin(admin.TabularInline):
    model = CategoryImage
    extra = 1


@admin.register(Category, site=rudik_site)
class CategoryAdmin(MPTTModelAdmin):
    inlines = [CategoryImageAdmin]


@admin.register(Product, site=rudik_site)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]
