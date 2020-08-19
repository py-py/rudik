from rest_framework import serializers
from rest_framework import viewsets
from rest_framework_recursive.fields import RecursiveField

from .models import Category
from .models import Product


class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True)

    class Meta:
        model = Category
        fields = ["id", "name", "children"]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.root_nodes()
    serializer_class = CategorySerializer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "category"]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
