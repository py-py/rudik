from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from rudik.admin import rudik_site

from .forms import ProductVariantModelForm
from .models import Category
from .models import CategoryImage
from .models import Color
from .models import Configuration
from .models import ConfigurationType
from .models import Product
from .models import ProductImage
from .models import ProductVariant


class ImageMixin(object):
    def get_queryset(self, request):
        qs = super(ImageMixin, self).get_queryset(request)
        return qs.order_by("-is_default")

    class Media:
        js = (
            "admin/js/jquery.init.js",
            "product/js/is_default.js",
        )


@admin.register(Color, site=rudik_site)
class ColorAdmin(admin.ModelAdmin):
    list_display = ["__str__", "color"]


class CategoryImageTabularInline(ImageMixin, admin.TabularInline):
    model = CategoryImage
    extra = 1


@admin.register(Category, site=rudik_site)
class CategoryAdmin(MPTTModelAdmin):
    inlines = [CategoryImageTabularInline]


class ProductImageTabularInline(ImageMixin, admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product, site=rudik_site)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageTabularInline]


@admin.register(ConfigurationType, site=rudik_site)
class ConfigurationTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Configuration, site=rudik_site)
class ConfigurationAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductVariant, site=rudik_site)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ["__str__", "configs", "qty"]
    form = ProductVariantModelForm

    def configs(self, obj):
        return ", ".join(str(config) for config in obj.configurations.all())
