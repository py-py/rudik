from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.urls import reverse
from mptt.admin import MPTTModelAdmin

from rudik.admin import rudik_site

from .forms import ProductVariantModelForm
from .models import Category
from .models import CategoryImage
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
    class Media:
        js = (
            "admin/js/jquery.init.js",
            "configuration/js/change_type.js",
        )

    def get_urls(self):
        urls = super(ConfigurationAdmin, self).get_urls()
        return [path("is_color/", self.is_color_type, name="is_color_type")] + urls

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super(ConfigurationAdmin, self).get_form(request, obj, change, **kwargs)
        form.base_fields["type"].widget.attrs["data-url"] = reverse("admin:is_color_type")
        return form

    def is_color_type(self, request):
        try:
            type_id = int(request.GET["type_id"])
            config_type = ConfigurationType.objects.get(id=type_id)
            is_color = config_type.is_color
        except Exception:
            is_color = False
        return JsonResponse({"isColor": is_color})


@admin.register(ProductVariant, site=rudik_site)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ["__str__", "configs", "qty", "price", "cost", "margin"]
    form = ProductVariantModelForm

    def configs(self, obj):
        return ", ".join(str(config) for config in obj.configurations.all())