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
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = super(CategoryViewSet, self).get_queryset()
        if self.action == "list":
            return Category.objects.root_nodes()
        return queryset


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "category"]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ["category"]
