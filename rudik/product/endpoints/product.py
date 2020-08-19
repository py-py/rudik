from rest_framework import serializers
from rest_framework import viewsets

from ..models import Product
from ..models import ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "is_default"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)

    class Meta:
        model = Product
        fields = ["id", "name", "category", "images"]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ["category"]
