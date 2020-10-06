from rest_framework import serializers
from rest_framework import viewsets

from core.paginations import SmallPageNumberPagination

from ..models import Configuration
from ..models import ConfigurationType
from ..models import Product
from ..models import ProductImage
from ..models import ProductVariant


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "is_default"]


class ConfigurationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigurationType
        fields = ["id", "name", "is_color"]


class ConfigurationSerializer(serializers.ModelSerializer):
    type = ConfigurationTypeSerializer()

    class Meta:
        model = Configuration
        fields = ["id", "type", "name", "value", "type"]


class ProductVariantSerializer(serializers.ModelSerializer):
    configurations = ConfigurationSerializer(many=True)
    qty = serializers.IntegerField(source="count_rest")

    class Meta:
        model = ProductVariant
        fields = ["id", "qty", "price", "configurations"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)
    variants = ProductVariantSerializer(many=True)

    class Meta:
        model = Product
        fields = ["id", "name", "category", "images", "variants"]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.order_by("id")
    serializer_class = ProductSerializer
    pagination_class = SmallPageNumberPagination
    filterset_fields = ["category"]
